from unittest.mock import patch
import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from apps.patient.models import Patient


@pytest.mark.django_db
class TestPatientAPI:
    def test_get_me_unauthorized(self, api_client):
        assert api_client.get(reverse("patient_me")).status_code == 401

    def test_get_me_not_found(self, api_client, valid_jwt):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {valid_jwt}")
        assert api_client.get(reverse("patient_me")).status_code == 404

    @patch("apps.patient.views.publicar_evento")
    def test_create_and_get_me(self, mock_publish, api_client, valid_jwt):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {valid_jwt}")
        response = api_client.patch(reverse("patient_me"), {
            "cedula": "0102030405", "blood_type": "O+", "consent_data": True,
            "allergies": ["penicilina"],
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "cedula" not in response.data and "cedula_encrypted" not in response.data
        assert Patient.objects.get().cedula_encrypted != b"0102030405"
        assert api_client.get(reverse("patient_me")).status_code == 200
        mock_publish.assert_called_once()

    @patch("apps.patient.views.publicar_evento")
    def test_patch_me(self, mock_publish, api_client, valid_jwt, patient):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {valid_jwt}")
        response = api_client.patch(reverse("patient_me"), {"blood_type": "A+"}, format="json")
        assert response.status_code == 200
        assert response.data["blood_type"] == "A+"

    def test_summary_m2m_unauthorized(self, api_client, patient):
        url = reverse("patient_summary", kwargs={"pk": patient.pk})
        assert api_client.get(url).status_code == 401

    def test_summary_m2m_authorized(self, api_client, patient):
        api_client.credentials(HTTP_X_SERVICE_TOKEN=settings.SERVICE_TOKEN)
        response = api_client.get(reverse("patient_summary", kwargs={"pk": patient.pk}))
        assert response.status_code == 200
        assert response.data["blood_type"] == "O+"
        assert "cedula_encrypted" not in response.data
