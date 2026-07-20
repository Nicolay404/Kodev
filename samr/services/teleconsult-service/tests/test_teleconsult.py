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
