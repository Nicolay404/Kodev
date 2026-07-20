import datetime
import uuid
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from rest_framework.test import APIClient


@pytest.fixture(scope="session")
def rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture(autouse=True)
def mock_jwt_keys(monkeypatch, tmp_path, rsa_keys):
    path = tmp_path / "public.pem"
    path.write_bytes(rsa_keys[1].public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", str(path))


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def patient_id():
    return uuid.uuid4()


def _jwt(private_key, role, user_id):
    return jwt.encode({"usuario_id": str(user_id), "email": f"{role}@test.com", "rol": role, "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)}, private_key, algorithm="RS256")


@pytest.fixture
def patient_jwt(rsa_keys, patient_id):
    return _jwt(rsa_keys[0], "patient", patient_id)


@pytest.fixture
def admin_jwt(rsa_keys):
    return _jwt(rsa_keys[0], "system_admin", uuid.uuid4())
