import uuid
from unittest.mock import patch
import pytest
from django.urls import reverse
from apps.teleconsult.models import TeleconsultSession


@pytest.mark.django_db
class TestTeleconsultAPI:
    @patch("apps.teleconsult.views.publicar_evento")
    def test_create_session(self, mock_publish, api_client, auth_jwt_medical):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        response = api_client.post(reverse("teleconsult_create"), {"patient_id": str(uuid.uuid4())}, format="json")
        assert response.status_code == 201
        session = TeleconsultSession.objects.get()
        assert session.status == "active" and session.room_token
        mock_publish.assert_called_once()

    def test_create_session_unauthorized(self, api_client):
        assert api_client.post(reverse("teleconsult_create"), {"patient_id": str(uuid.uuid4())}, format="json").status_code == 401

    def test_patient_lists_and_reads_only_own_sessions(self, api_client, patient_jwt, patient_id):
        own = TeleconsultSession.objects.create(patient_id=patient_id, professional_id=uuid.uuid4())
        hidden = TeleconsultSession.objects.create(patient_id=uuid.uuid4(), professional_id=uuid.uuid4())
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")

        listed = api_client.get(reverse("teleconsult_create"))

        assert listed.status_code == 200 and [item["id"] for item in listed.data] == [str(own.id)]
        assert api_client.get(reverse("teleconsult_detail", kwargs={"session_id": own.id})).status_code == 200
        assert api_client.get(reverse("teleconsult_detail", kwargs={"session_id": hidden.id})).status_code == 403

    @patch("apps.teleconsult.views.publicar_evento")
    def test_assigned_professional_closes_and_publishes_event(self, mock_publish, api_client, professional_jwt, professional_id, patient_id):
        session = TeleconsultSession.objects.create(patient_id=patient_id, professional_id=professional_id)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {professional_jwt}")

        response = api_client.post(reverse("teleconsult_close", kwargs={"session_id": session.id}), {"diagnosis": "Evaluación completada"}, format="json")

        assert response.status_code == 200 and response.data["status"] == "closed"
        assert response.data["closed_at"] is not None
        assert mock_publish.call_args.args[0] == "teleconsult.closed"
        assert mock_publish.call_args.args[1]["patient_id"] == str(patient_id)

    def test_patient_cannot_close_session(self, api_client, patient_jwt, patient_id):
        session = TeleconsultSession.objects.create(patient_id=patient_id, professional_id=uuid.uuid4())
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        assert api_client.post(reverse("teleconsult_close", kwargs={"session_id": session.id}), {"diagnosis": "x"}, format="json").status_code == 403
