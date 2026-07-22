from unittest.mock import patch
import uuid
import pytest
from django.test import override_settings
from django.urls import reverse
from apps.solicitud.models import Conversation, FAQ, Solicitud
from tasks.validate_with_consortium import validate_with_consortium


@pytest.mark.django_db
class TestSolicitudAPI:
    def test_faq_list(self, api_client, patient_jwt):
        FAQ.objects.create(question="dolor de cabeza", answer="Consulte a un profesional")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        assert len(api_client.get(reverse("faq")).data) == 1

    def test_faq_create_admin(self, api_client, admin_jwt):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_jwt}")
        response = api_client.post(reverse("faq"), {"question": "Q", "answer": "A"}, format="json")
        assert response.status_code == 201

    def test_faq_create_patient_forbidden(self, api_client, patient_jwt):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        assert api_client.post(reverse("faq"), {"question": "Q", "answer": "A"}, format="json").status_code == 403

    @patch("apps.solicitud.views.publicar_evento")
    def test_chat_faq_and_fallback(self, mock_publish, api_client, patient_jwt):
        FAQ.objects.create(question="tengo dolor de cabeza fuerte", answer="Respuesta FAQ verificada")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        response = api_client.post(reverse("chat"), {"message": "tengo dolor de cabeza fuerte"}, format="json")
        assert response.status_code == 200
        assert response.data["source"] == "faq"
        fallback = api_client.post(reverse("chat"), {"message": "consulta sin coincidencia"}, format="json")
        assert fallback.data["source"] == "human_escalation"

    def test_conversation_delete_owner(self, api_client, patient_jwt, patient_id):
        conversation = Conversation.objects.create(patient_id=patient_id)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        response = api_client.delete(reverse("conversation_delete", kwargs={"id": conversation.id}))
        assert response.status_code == 204

    @patch("apps.solicitud.views.publicar_evento")
    @patch("apps.solicitud.views.validate_with_consortium.delay")
    def test_create_solicitud(self, mock_task, mock_publish, api_client, patient_jwt):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        response = api_client.post(reverse("solicitud_create"), {"sintomas": ["dolor"], "fuente": "manual"}, format="json")
        assert response.status_code == 201
        assert Solicitud.objects.get().estado == "pendiente"
        mock_task.assert_called_once()

    def test_list_and_detail_only_include_owner(self, api_client, patient_jwt, patient_id):
        own = Solicitud.objects.create(patient_id=patient_id, sintomas=["dolor"])
        Solicitud.objects.create(patient_id=uuid.uuid4(), sintomas=["fiebre"])
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")

        listed = api_client.get(reverse("solicitud_create"))
        detail = api_client.get(reverse("solicitud_detail", kwargs={"id": own.id}))

        assert listed.status_code == 200 and [item["id"] for item in listed.data] == [str(own.id)]
        assert detail.status_code == 200 and detail.data["id"] == str(own.id)

    def test_detail_hides_another_patients_request(self, api_client, patient_jwt):
        solicitud = Solicitud.objects.create(patient_id=uuid.uuid4(), sintomas=["dolor"])
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {patient_jwt}")
        assert api_client.get(reverse("solicitud_detail", kwargs={"id": solicitud.id})).status_code == 404

    @patch("tasks.validate_with_consortium.publicar_evento")
    @override_settings(MVP_CONSORTIUM_OUTCOME="validated")
    def test_consortium_adapter_validates(self, mock_publish, patient_id):
        solicitud = Solicitud.objects.create(patient_id=patient_id, sintomas=["dolor"])
        assert validate_with_consortium(str(solicitud.id)) == "validada"
        solicitud.refresh_from_db()
        assert solicitud.estado == "validada"

    @override_settings(MVP_CONSORTIUM_OUTCOME="timeout")
    def test_consortium_timeout_pending_retry(self, patient_id):
        solicitud = Solicitud.objects.create(patient_id=patient_id, sintomas=["dolor"])
        assert validate_with_consortium(str(solicitud.id)) == "pending_retry"
        solicitud.refresh_from_db()
        assert solicitud.estado == "pendiente_reintento"
