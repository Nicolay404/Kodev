import pytest
from django.urls import reverse
from rest_framework import status
from django.conf import settings
from apps.evaluacion.models import Evaluacion
from unittest.mock import patch

@pytest.mark.django_db
class TestEvaluacionAPI:

    def test_get_riesgo(self, api_client, auth_jwt):
        Evaluacion.objects.create(solicitud_id=123, riesgo_score=0.85)
        url = reverse('riesgo', kwargs={'solicitud_id': 123})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['riesgo_score'] == 0.85
        
    def test_get_riesgo_unauthorized(self, api_client):
        url = reverse('riesgo', kwargs={'solicitud_id': 123})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_centros_disponibles(self, api_client):
        url = reverse('centros_disponibles')
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.SERVICE_TOKEN)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        
    @patch('apps.evaluacion.views.publicar_evento')
    def test_matching(self, mock_publish, api_client, auth_jwt):
        ev = Evaluacion.objects.create(solicitud_id=124, riesgo_score=0.5)
        url = reverse('matching', kwargs={'evaluacion_id': ev.id})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt}')
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'centro_asignado' in response.data
        mock_publish.assert_called_once()
