from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from apps.auth.models import User


@pytest.mark.django_db
class TestAuthAPI:
    def test_register(self, api_client):
        response = api_client.post(
            reverse("register"),
            {"email": "newuser@example.com", "password": "secure123"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_register_cannot_escalate_role(self, api_client):
        response = api_client.post(
            reverse("register"),
            {
                "email": "patient@example.com",
                "password": "secure123",
                "role": "system_admin",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.get(email="patient@example.com").role == "patient"

    def test_register_rejects_non_alphanumeric_password(self, api_client):
        response = api_client.post(
            reverse("register"),
            {"email": "weak@example.com", "password": "onlyletters"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.auth.views.publicar_evento")
    def test_login(self, mock_publish, api_client, create_user, user_data):
        response = api_client.post(reverse("login"), user_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data
        create_user.refresh_from_db()
        assert create_user.failed_attempts == 0
        mock_publish.assert_called_once()

    @patch("apps.auth.views.publicar_evento")
    def test_refresh_token(self, mock_publish, api_client, create_user, user_data):
        login = api_client.post(reverse("login"), user_data, format="json")
        response = api_client.post(
            reverse("token_refresh"),
            {"refresh_token": login.data["refresh_token"]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

    @patch("apps.auth.views.publicar_evento")
    def test_me(self, mock_publish, api_client, create_user, user_data):
        login = api_client.post(reverse("login"), user_data, format="json")
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login.data['access_token']}"
        )
        response = api_client.get(reverse("me"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user_data["email"]

    @patch("apps.auth.views.publicar_evento")
    def test_login_blocked(self, mock_publish, api_client, create_user, user_data):
        wrong = {"email": user_data["email"], "password": "wrong123"}
        for _ in range(5):
            response = api_client.post(reverse("login"), wrong, format="json")
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response = api_client.post(reverse("login"), user_data, format="json")
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        create_user.refresh_from_db()
        assert create_user.failed_attempts == 5
        assert create_user.locked_until is not None
