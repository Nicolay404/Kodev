import pytest
from django.urls import reverse
from rest_framework import status
from apps.solicitud.models import FAQ, Conversation, Solicitud
from unittest.mock import patch

@pytest.mark.django_db
class TestSolicitudAPI:

    def test_faq_list(self, api_client, patient_jwt):
        FAQ.objects.create(question='Q1', answer='A1')
        url = reverse('faq')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {patient_jwt}')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_faq_create_admin(self, api_client, admin_jwt):
        url = reverse('faq')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_jwt}')
        data = {'question': 'Q', 'answer': 'A'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_faq_create_patient_forbidden(self, api_client, patient_jwt):
        url = reverse('faq')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {patient_jwt}')
        data = {'question': 'Q', 'answer': 'A'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_chat(self, api_client, patient_jwt):
        url = reverse('chat')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {patient_jwt}')
        data = {'message': 'Hola'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'chat_id' in response.data
        assert 'response' in response.data

    def test_conversation_delete(self, api_client, patient_jwt):
        conv = Conversation.objects.create(patient_id=100)
        url = reverse('conversation_delete', kwargs={'id': conv.id})
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {patient_jwt}')
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Conversation.objects.filter(id=conv.id).exists()

    @patch('apps.solicitud.views.validate_with_consortium.delay')
    def test_create_solicitud(self, mock_task, api_client, patient_jwt):
        url = reverse('solicitud_create')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {patient_jwt}')
        data = {
            'description': 'Dolor de cabeza',
            'symptoms': ['dolor'],
            'urgency': 'low'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Solicitud.objects.count() == 1
        assert Solicitud.objects.first().estado == 'pendiente'
        mock_task.assert_called_once()
