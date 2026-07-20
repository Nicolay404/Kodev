import uuid
from unittest.mock import patch
import pytest
from django.conf import settings
from django.urls import reverse
from apps.evaluacion.models import AvailableCenterCache, Evaluacion, Matching
from tasks.procesar_solicitud import procesar_solicitud_validada


@pytest.mark.django_db
class TestEvaluacionAPI:
    def test_get_riesgo(self, api_client, auth_jwt):
        solicitud_id = uuid.uuid4()
        Evaluacion.objects.create(solicitud_id=solicitud_id, nivel_riesgo="medio")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt}")
        response = api_client.get(reverse("riesgo", kwargs={"solicitud_id": solicitud_id}))
        assert response.status_code == 200 and response.data["nivel_riesgo"] == "medio"

    def test_centros_disponibles(self, api_client):
        AvailableCenterCache.objects.create(center_id=uuid.uuid4(), nombre="Centro MVP", disponible=True)
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.SERVICE_TOKEN)
        response = api_client.get(reverse("centros_disponibles"))
        assert response.status_code == 200 and len(response.data) == 1

    @patch("apps.evaluacion.views.publicar_evento")
    def test_matching(self, mock_publish, api_client, auth_jwt):
        evaluation = Evaluacion.objects.create(solicitud_id=uuid.uuid4(), nivel_riesgo="medio")
        center = AvailableCenterCache.objects.create(center_id=uuid.uuid4(), nombre="Centro MVP")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt}")
        response = api_client.post(reverse("matching", kwargs={"evaluacion_id": evaluation.id}), {"patient_id": str(uuid.uuid4())}, format="json")
        assert response.status_code == 201
        assert Matching.objects.get().center_id == center.center_id

    @patch("tasks.procesar_solicitud.publicar_evento")
    def test_process_validated_request(self, mock_publish):
        solicitud_id = uuid.uuid4()
        result = procesar_solicitud_validada({"solicitud_id": str(solicitud_id), "sintomas": ["síntoma de prueba"]})
        assert uuid.UUID(result)
        assert Evaluacion.objects.get().nivel_riesgo == "medio"
        assert mock_publish.call_count == 2

    @patch("apps.evaluacion.views.publicar_evento")
    def test_matching_without_center(self, mock_publish, api_client, auth_jwt):
        evaluation = Evaluacion.objects.create(solicitud_id=uuid.uuid4(), nivel_riesgo="medio")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt}")
        response = api_client.post(reverse("matching", kwargs={"evaluacion_id": evaluation.id}), {"patient_id": str(uuid.uuid4())}, format="json")
        assert response.status_code == 409
        mock_publish.assert_called_once_with("matching.fallido", {"evaluacion_id": str(evaluation.id), "reason": "no_available_center"})
