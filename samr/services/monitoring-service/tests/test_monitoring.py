import pytest
from django.urls import reverse
from rest_framework import status
from apps.monitoring.models import IoTReading, Alert
from unittest.mock import AsyncMock, patch

@pytest.mark.django_db
class TestMonitoringAPI:

    @patch('apps.monitoring.views.publicar_evento')
    @patch('apps.monitoring.views.get_channel_layer')
    def test_post_iot_reading(self, mock_channel_layer, mock_publish, api_client):
        mock_channel_layer.return_value.group_send = AsyncMock()
        url = reverse('iot_events')
        api_client.credentials(HTTP_X_DEVICE_TOKEN='DEV-12345')
        
        data = {
            'device_id': 'dev_01',
            'patient_id': 100,
            'vitals': {
                'heart_rate': 120, # This will trigger anomaly (>110)
                'oxygen_level': 98
            }
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert IoTReading.objects.count() == 1
        assert Alert.objects.count() == 1
        
        # Verificamos que se publicaron eventos
        mock_publish.assert_called_once()
        
    def test_post_iot_reading_unauthorized(self, api_client):
        url = reverse('iot_events')
        # Sin header o con header inválido
        response = api_client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_alerts(self, api_client, auth_jwt):
        Alert.objects.create(patient_id=100, tipo='Abnormal Heart Rate')
        url = reverse('alerts')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt}')
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
