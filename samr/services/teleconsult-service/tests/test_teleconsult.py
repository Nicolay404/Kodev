import pytest
from django.urls import reverse
from rest_framework import status
from apps.teleconsult.models import TeleconsultSession
from unittest.mock import patch

@pytest.mark.django_db
class TestTeleconsultAPI:

    @patch('apps.teleconsult.views.publicar_evento')
    def test_create_session(self, mock_publish, api_client, auth_jwt_medical):
        url = reverse('teleconsult_create')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        
        data = {
            'patient_id': 100
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert TeleconsultSession.objects.count() == 1
        
        session = TeleconsultSession.objects.first()
        assert session.doctor_id == 200 # Sacado del JWT
        assert session.room_token is not None
        
        mock_publish.assert_called_once()
        
    def test_create_session_unauthorized(self, api_client):
        url = reverse('teleconsult_create')
        response = api_client.post(url, {'patient_id': 100}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
