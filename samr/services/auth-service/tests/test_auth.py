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

    @patch("apps.auth.views.publicar_evento")
    def test_password_change_requires_current_password(self, mock_publish, api_client, create_user, user_data):
        login = api_client.post(reverse("login"), user_data, format="json")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access_token']}")
        denied = api_client.post(reverse("password_change"), {"current_password": "wrong123", "new_password": "changed123"}, format="json")
        changed = api_client.post(reverse("password_change"), {"current_password": user_data["password"], "new_password": "changed123"}, format="json")
        assert denied.status_code == 400 and changed.status_code == 200
        create_user.refresh_from_db()
        assert create_user.check_password("changed123")

    @patch("apps.auth.views.publicar_evento")
    def test_password_reset_is_generic_and_token_is_single_use(self, mock_publish, api_client, create_user):
        requested = api_client.post(reverse("password_reset_request"), {"email": create_user.email}, format="json")
        token = mock_publish.call_args.args[1]["reset_token"]
        reset = api_client.post(reverse("password_reset_confirm"), {"token": token, "new_password": "recovered123"}, format="json")
        reused = api_client.post(reverse("password_reset_confirm"), {"token": token, "new_password": "another123"}, format="json")
        unknown = api_client.post(reverse("password_reset_request"), {"email": "missing@example.com"}, format="json")
        assert requested.status_code == 202 and unknown.status_code == 202
        assert requested.data == unknown.data
        assert reset.status_code == 200 and reused.status_code == 400
        create_user.refresh_from_db()
        assert create_user.check_password("recovered123")
