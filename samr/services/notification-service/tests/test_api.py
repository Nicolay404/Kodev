import datetime
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.test import Client
from django.urls import reverse


class FakeInbox:
    notification = {
        "id": "11111111-1111-4111-8111-111111111111",
        "event_type": "recursos.asignados",
        "payload": {"patient_id": "22222222-2222-4222-8222-222222222222"},
        "read": False,
        "created_at": "2026-07-21T00:00:00+00:00",
    }

    def list_for(self, recipient_id):
        return [self.notification]

    def mark_read(self, recipient_id, notification_id):
        return {**self.notification, "read": True} if str(notification_id) == self.notification["id"] else None


@pytest.fixture
def auth_header(monkeypatch, tmp_path):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_path = tmp_path / "public.pem"
    public_path.write_bytes(private_key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", str(public_path))
    token = jwt.encode(
        {
            "usuario_id": str(uuid.uuid4()), "rol": "patient", "type": "access",
            "iss": "samr-auth-service",
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15),
        },
        private_key,
        algorithm="RS256",
    )
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def fake_inbox(monkeypatch):
    monkeypatch.setattr("apps.notifications.views.get_inbox", lambda: FakeInbox())


def test_list_notifications_requires_jwt(auth_header):
    client = Client()
    assert client.get(reverse("notification_list")).status_code == 401
    response = client.get(reverse("notification_list"), **auth_header)
    assert response.status_code == 200 and len(response.json()) == 1


def test_mark_notification_read(auth_header):
    client = Client()
    response = client.patch(
        reverse("notification_mark_read", kwargs={"notification_id": FakeInbox.notification["id"]}),
        data="{}", content_type="application/json", **auth_header,
    )
    assert response.status_code == 200 and response.json()["read"] is True
