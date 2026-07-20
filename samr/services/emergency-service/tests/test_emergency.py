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
