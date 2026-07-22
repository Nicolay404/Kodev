import uuid
from unittest.mock import patch
import pytest
from django.urls import reverse
from apps.emergency.models import Emergency, FirstAidGuide


@pytest.mark.django_db
class TestEmergencyAPI:
    @patch("apps.emergency.views.publicar_evento")
    def test_create_emergency(self, mock_publish, api_client, auth_jwt_patient):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_patient}")
        response = api_client.post(reverse("emergency_list"), {"triage_level": "critico"}, format="json")
        assert response.status_code == 201
        assert Emergency.objects.count() == 1 and FirstAidGuide.objects.count() == 1
        assert mock_publish.call_count == 2

    @patch("apps.emergency.views.publicar_evento")
    def test_dispatch_emergency(self, mock_publish, api_client, auth_jwt_medical):
        emergency = Emergency.objects.create(patient_id=uuid.uuid4(), triage_level="alto")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_medical}")
        response = api_client.post(reverse("emergency_dispatch", kwargs={"emergency_id": emergency.id}))
        assert response.status_code == 200
        emergency.refresh_from_db(); assert emergency.status == "dispatched"

    def test_dispatch_forbidden(self, api_client, auth_jwt_patient):
        emergency = Emergency.objects.create(patient_id=uuid.uuid4(), triage_level="alto")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_patient}")
        assert api_client.post(reverse("emergency_dispatch", kwargs={"emergency_id": emergency.id})).status_code == 403

    def test_patient_reads_own_emergency_detail(self, api_client, auth_jwt_patient, patient_id):
        own = Emergency.objects.create(patient_id=patient_id, triage_level="alto")
        hidden = Emergency.objects.create(patient_id=uuid.uuid4(), triage_level="medio")
        FirstAidGuide.objects.create(emergency=own, contenido="Guía MVP")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_patient}")
        response = api_client.get(reverse("emergency_detail", kwargs={"emergency_id": own.id}))
        assert response.status_code == 200 and response.data["guides"][0]["contenido"] == "Guía MVP"
        assert api_client.get(reverse("emergency_detail", kwargs={"emergency_id": hidden.id})).status_code == 403
