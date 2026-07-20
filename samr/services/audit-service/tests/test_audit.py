import pytest
from django.urls import reverse
from rest_framework import status
from apps.audit.models import DecisionIA
from tasks.procesar_auditoria import procesar_riesgo_evaluado

@pytest.mark.django_db
class TestAuditAPI:

    def test_get_decisions_success(self, api_client, auth_jwt_dpd):
        DecisionIA.objects.create(solicitud_id=1, decision={'risk': 'high'})
        url = reverse('audit_decisions')
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_dpd}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        
    def test_get_decisions_forbidden(self, api_client, auth_jwt_admin):
        # Admin NO es dpd_delegate
        url = reverse('audit_decisions')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_admin}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_review_decision(self, api_client, auth_jwt_dpd):
        log = DecisionIA.objects.create(solicitud_id=1, decision={'risk': 'high'})
        url = reverse('audit_review', kwargs={'audit_log_id': log.id})
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_jwt_dpd}')
        data = {'review_notes': 'Decisión validada conforme a protocolo LOPDP'}
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        log.refresh_from_db()
        assert log.reviewed == True
        assert log.reviewed_by == 500

    def test_task_procesar_riesgo_evaluado(self):
        # Prueba de la tarea asíncrona
        procesar_riesgo_evaluado({
            'solicitud_id': 100,
            'evaluacion_id': 50,
            'decision': {'risk': 'low'},
            'context': {'symptoms': 'headache'}
        })
        
        assert DecisionIA.objects.count() == 1
        d = DecisionIA.objects.first()
        assert d.solicitud_id == 100
        assert d.decision['risk'] == 'low'
