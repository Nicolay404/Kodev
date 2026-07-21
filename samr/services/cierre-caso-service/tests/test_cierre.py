import uuid
from unittest.mock import patch
import pytest
from django.urls import reverse
from apps.cierre.models import Caso


@pytest.mark.django_db
class TestCierreCasoAPI:
    @patch("apps.cierre.views.publicar_evento")
    def test_close_case_with_integrity(self, mock_publish, api_client, auth_jwt_medical):
        case = Caso.objects.create(patient_id=uuid.uuid4(), emergency_id=uuid.uuid4())
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        response = api_client.post(reverse("cierre_close", kwargs={"caso_id": case.id}), {"clinical_notes": "Atención completada"}, format="json")
        assert response.status_code == 200
        case.refresh_from_db(); assert case.status == "closed" and len(case.integrity_hash) == 64

    def test_close_without_source_rejected(self, api_client, auth_jwt_medical):
        case = Caso.objects.create(patient_id=uuid.uuid4())
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        assert api_client.post(reverse("cierre_close", kwargs={"caso_id": case.id}), {"clinical_notes": "Notas"}, format="json").status_code == 409

    def test_verify_case(self, api_client, auth_jwt_medical):
        case = Caso.objects.create(patient_id=uuid.uuid4(), teleconsult_id=uuid.uuid4(), clinical_notes="Notas")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        response = api_client.get(reverse("cierre_verify", kwargs={"caso_id": case.id}))
        assert response.status_code == 200 and response.data["ready_to_close"] is True
