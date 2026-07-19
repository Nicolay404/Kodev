import pytest
from django.urls import reverse
from rest_framework import status
from apps.emergency.models import Emergency
from unittest.mock import patch

@pytest.mark.django_db
class TestEmergencyAPI:

    def test_create_emergency(self, api_client, auth_jwt_patient):
        url = reverse('emergency_list')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_patient}')
        
        data = {
            'description': 'Heart attack symptoms',
            'location': {'lat': -0.18, 'lng': -78.46}
        }
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Emergency.objects.count() == 1
        
        em = Emergency.objects.first()
        assert em.patient_id == 100
        assert em.status == 'reported'

    @patch('apps.emergency.views.publicar_evento')
    def test_dispatch_emergency(self, mock_publish, api_client, auth_jwt_medical):
        em = Emergency.objects.create(patient_id=100, description="Test")
        url = reverse('emergency_dispatch', kwargs={'emergency_id': em.id})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        em.refresh_from_db()
        assert em.status == 'dispatched'
        assert em.dispatched_at is not None
        
        mock_publish.assert_called_once()
        
    def test_dispatch_emergency_forbidden(self, api_client, auth_jwt_patient):
        em = Emergency.objects.create(patient_id=100, description="Test")
        url = reverse('emergency_dispatch', kwargs={'emergency_id': em.id})
        
        # Paciente no puede despachar
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_patient}')
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
