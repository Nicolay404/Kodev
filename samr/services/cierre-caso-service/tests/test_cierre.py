import pytest
from django.urls import reverse
from rest_framework import status
from apps.cierre.models import Caso
from unittest.mock import patch

@pytest.mark.django_db
class TestCierreCasoAPI:

    @patch('apps.cierre.views.publicar_evento')
    def test_close_caso_success(self, mock_publish, api_client, auth_jwt_medical):
        caso = Caso.objects.create(patient_id=100)
        url = reverse('cierre_close', kwargs={'caso_id': caso.id})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        data = {'notes': 'Patient recovered successfully.'}
        
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        caso.refresh_from_db()
        assert caso.status == 'closed'
        assert caso.closed_at is not None
        mock_publish.assert_called_once()
        
    def test_close_caso_forbidden(self, api_client, auth_jwt_patient):
        caso = Caso.objects.create(patient_id=100)
        url = reverse('cierre_close', kwargs={'caso_id': caso.id})
        
        # Paciente no puede cerrar el caso
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_patient}')
        response = api_client.post(url, {'notes': 'test'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_verify_caso(self, api_client, auth_jwt_medical):
        caso = Caso.objects.create(patient_id=100, notes="Triage done")
        url = reverse('cierre_verify', kwargs={'caso_id': caso.id})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['ready_to_close'] == True
