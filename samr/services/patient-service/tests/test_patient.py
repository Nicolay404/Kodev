import pytest
from django.urls import reverse
from rest_framework import status
from django.conf import settings

@pytest.mark.django_db
class TestPatientAPI:
    
    def test_get_me_unauthorized(self, api_client):
        url = reverse('patient_me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_not_found(self, api_client, valid_jwt):
        url = reverse('patient_me')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_jwt}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_and_get_me(self, api_client, valid_jwt):
        url = reverse('patient_me')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_jwt}')
        
        # Create (PATCH creates if doesn't exist)
        data = {
            'full_name': 'New Patient',
            'age': 25,
            'gender': 'Female',
            'gdpr_consent': True
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # Get
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'New Patient'

    def test_patch_me(self, api_client, valid_jwt, patient):
        url = reverse('patient_me')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {valid_jwt}')
        
        data = {'age': 31}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['age'] == 31

    def test_summary_m2m_unauthorized(self, api_client, patient):
        url = reverse('patient_summary', kwargs={'pk': patient.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_summary_m2m_authorized(self, api_client, patient):
        url = reverse('patient_summary', kwargs={'pk': patient.pk})
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.SERVICE_TOKEN)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'full_name' in response.data
        assert 'created_at' not in response.data # Not in summary
