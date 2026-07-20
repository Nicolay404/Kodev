import pytest
from django.urls import reverse
from rest_framework import status
from apps.admin_integ.models import Center, Device
from unittest.mock import patch
from django.conf import settings

@pytest.mark.django_db
class TestAdminAPI:

    @patch('apps.admin_integ.views.publicar_evento')
    def test_register_center(self, mock_publish, api_client, auth_jwt_sysadmin):
        url = reverse('center_register')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_sysadmin}')
        
        data = {
            'name': 'Hospital Metropolitano',
            'location': {'lat': -0.18, 'lng': -78.46},
            'max_capacity': 100,
            'current_occupancy': 50
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Center.objects.count() == 1
        mock_publish.assert_called_once()
        
    def test_register_center_forbidden(self, api_client, auth_jwt_medical):
        # Médico no puede registrar centro (requiere system_admin)
        url = reverse('center_register')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        response = api_client.post(url, {'name': 'Test'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_available_centers_m2m(self, api_client):
        # Creamos dos centros, solo uno con capacidad
        Center.objects.create(name='H1', max_capacity=10, current_occupancy=10)
        Center.objects.create(name='H2', max_capacity=10, current_occupancy=5)
        
        url = reverse('center_available')
        
        # Test con Service Token M2M
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.SERVICE_TOKEN)
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'H2'

    @patch('apps.admin_integ.views.publicar_evento')
    def test_register_device(self, mock_publish, api_client, auth_jwt_sysadmin):
        url = reverse('device_register')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_sysadmin}')
        
        data = {
            'mac_address': '00:11:22:33:44:55',
            'patient_id': 100,
            'device_type': 'heart_monitor'
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Device.objects.count() == 1
        mock_publish.assert_called_once()
