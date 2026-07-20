import uuid
from unittest.mock import patch
import pytest
from django.conf import settings
from django.urls import reverse
from apps.admin_integ.models import Center, Device


@pytest.mark.django_db
class TestAdminAPI:
    @patch("apps.admin_integ.views.validate_center_m2m.delay")
    @patch("apps.admin_integ.views.publicar_evento")
    def test_register_center(self, mock_publish, mock_task, api_client, auth_jwt_sysadmin):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_sysadmin}")
        response = api_client.post(reverse("center_register"), {"name": "Centro MVP", "type": "hospital", "latitude": "-0.180000", "longitude": "-78.460000", "license_number": "MVP-001", "specialties": ["general"]}, format="json")
        assert response.status_code == 201 and Center.objects.get().status == "pending_validation"

    def test_available_centers_m2m(self, api_client):
        Center.objects.create(name="Validado", status="validated"); Center.objects.create(name="Pendiente")
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.SERVICE_TOKEN)
        assert len(api_client.get(reverse("center_available")).data) == 1

    @patch("apps.admin_integ.views.publicar_evento")
    def test_register_device(self, mock_publish, api_client, auth_jwt_sysadmin):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt_sysadmin}")
        response = api_client.post(reverse("device_register"), {"patient_id": str(uuid.uuid4()), "device_type": "oximeter", "serial_number": "SER-001"}, format="json")
        assert response.status_code == 201 and Device.objects.count() == 1
