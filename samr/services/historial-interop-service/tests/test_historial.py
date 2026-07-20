import pytest
from django.urls import reverse
from rest_framework import status
from apps.historial.models import Historial, Consentimiento
from tasks.procesar_historial import procesar_caso_cerrado

@pytest.mark.django_db
class TestHistorialAPI:

    def test_get_historial_success(self, api_client, auth_jwt_medical):
        Historial.objects.create(patient_id=100, data=[{'test': 'data'}])
        url = reverse('historial_get', kwargs={'patient_id': 100})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        
    def test_get_historial_forbidden(self, api_client, auth_jwt_patient):
        # El paciente 100 intenta ver el historial del 101
        url = reverse('historial_get', kwargs={'patient_id': 101})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_patient}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_fhir_history_without_consent(self, api_client, auth_jwt_medical):
        # Existe historial pero no consentimiento
        Historial.objects.create(patient_id=100, data=[])
        Consentimiento.objects.create(patient_id=100, fhir_enabled=False)
        
        url = reverse('fhir_history', kwargs={'patient_id': 100})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_fhir_history_with_consent(self, api_client, auth_jwt_medical):
        Historial.objects.create(patient_id=100, data=[{'closed_at': '2023-01-01T12:00:00Z'}])
        Consentimiento.objects.create(patient_id=100, fhir_enabled=True)
        
        url = reverse('fhir_history', kwargs={'patient_id': 100})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_medical}')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['resourceType'] == 'Bundle'

    def test_task_procesar_caso_cerrado(self):
        # Prueba directa de la tarea asíncrona
        procesar_caso_cerrado({
            'patient_id': 100,
            'caso_id': 50,
            'closed_at': '2023-10-10T10:00:00Z',
            'notes': 'OK'
        })
        
        h = Historial.objects.get(patient_id=100)
        assert len(h.data) == 1
        assert h.data[0]['caso_id'] == 50
