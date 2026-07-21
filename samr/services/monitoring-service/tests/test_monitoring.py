from unittest.mock import AsyncMock, patch
import pytest
from django.conf import settings
from django.urls import reverse
from apps.monitoring.models import Alert, VitalSign
from apps.monitoring.services import register_device


@pytest.mark.django_db
class TestMonitoringAPI:
    @patch("apps.monitoring.views.cache_reading")
    @patch("apps.monitoring.views.publicar_evento")
    @patch("apps.monitoring.views.get_channel_layer")
    def test_post_iot_reading(self, mock_layer, mock_publish, mock_cache, api_client, patient_id, device_id):
        mock_layer.return_value.group_send = AsyncMock()
        register_device({"device_id": str(device_id), "patient_id": str(patient_id)})
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.MVP_DEVICE_SERVICE_TOKEN)
        response = api_client.post(reverse("iot_events"), {"device_id": str(device_id), "patient_id": str(patient_id), "value": {"resourceType": "Observation", "measurements": {"heart_rate": 120}}}, format="json")
        assert response.status_code == 201
        assert VitalSign.objects.count() == 1 and Alert.objects.count() == 1
        mock_publish.assert_called_once()

    def test_rejects_unregistered_device(self, api_client, patient_id, device_id):
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.MVP_DEVICE_SERVICE_TOKEN)
        response = api_client.post(reverse("iot_events"), {"device_id": str(device_id), "patient_id": str(patient_id), "value": {"resourceType": "Observation", "measurements": {}}}, format="json")
        assert response.status_code == 403

    def test_rejects_invalid_observation(self, api_client, patient_id, device_id):
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.MVP_DEVICE_SERVICE_TOKEN)
        response = api_client.post(reverse("iot_events"), {"device_id": str(device_id), "patient_id": str(patient_id), "value": {}}, format="json")
        assert response.status_code == 400

    def test_post_unauthorized(self, api_client):
        assert api_client.post(reverse("iot_events"), {}, format="json").status_code == 401

    def test_get_alerts(self, api_client, auth_jwt, patient_id):
        Alert.objects.create(patient_id=patient_id, severity="critical")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_jwt}")
        response = api_client.get(reverse("alerts"))
        assert response.status_code == 200 and len(response.data) == 1
