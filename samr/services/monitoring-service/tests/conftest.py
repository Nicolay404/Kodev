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
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key, key.public_key()


@pytest.fixture(autouse=True)
def jwt_key(monkeypatch, tmp_path, rsa_keys):
    path = tmp_path / "public.pem"
    path.write_bytes(rsa_keys[1].public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", str(path))


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def patient_id():
    return uuid.uuid4()


@pytest.fixture
def device_id():
    return uuid.uuid4()


@pytest.fixture
def auth_jwt(rsa_keys):
    return jwt.encode({"usuario_id": str(uuid.uuid4()), "email": "professional@test.com", "rol": "professional", "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)}, rsa_keys[0], algorithm="RS256")
