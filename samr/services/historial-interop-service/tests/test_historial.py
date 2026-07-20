import uuid
from unittest.mock import patch
import pytest
from django.urls import reverse
from apps.historial.models import Historial
from tasks.procesar_historial import procesar_caso_cerrado


@pytest.mark.django_db
class TestHistorialAPI:
    def test_get_history(self, api_client, auth_jwt_medical):
        patient_id = uuid.uuid4(); Historial.objects.create(patient_id=patient_id, eventos=[{"caso_id": str(uuid.uuid4())}])
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        assert api_client.get(reverse("historial_get", kwargs={"patient_id": patient_id})).status_code == 200

    @patch("apps.historial.views.verify_sharing_consent", return_value=True)
    @patch("apps.historial.views.compose_fhir_bundle")
    def test_fhir_with_consent(self, mock_bundle, mock_consent, api_client, auth_jwt_medical):
        patient_id = uuid.uuid4(); history = Historial.objects.create(patient_id=patient_id)
        mock_bundle.return_value = {"resourceType": "Bundle", "type": "collection"}
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        response = api_client.get(reverse("fhir_history", kwargs={"patient_id": patient_id}))
        assert response.status_code == 200 and response.data["resourceType"] == "Bundle"

    def test_consolidation_idempotent(self):
        payload = {"patient_id": str(uuid.uuid4()), "caso_id": str(uuid.uuid4()), "closed_at": "2026-01-01T00:00:00Z"}
        procesar_caso_cerrado(payload); procesar_caso_cerrado(payload)
        assert len(Historial.objects.get().eventos) == 1
