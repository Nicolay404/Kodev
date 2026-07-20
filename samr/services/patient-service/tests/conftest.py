import datetime
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from rest_framework.test import APIClient

from apps.patient.models import Patient
from apps.patient.services import encrypt_cedula


@pytest.fixture(scope="session")
def rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


@pytest.fixture(autouse=True)
def mock_jwt_keys(monkeypatch, tmp_path, rsa_keys):
    pub_path = tmp_path / "public.pem"
    pub_path.write_bytes(rsa_keys[1].public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", str(pub_path))


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def valid_jwt(rsa_keys, user_id):
    payload = {
        "usuario_id": str(user_id), "email": "test@patient.com", "rol": "patient",
        "type": "access", "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15),
    }
    return jwt.encode(payload, rsa_keys[0], algorithm="RS256")


@pytest.fixture
def patient(user_id):
    return Patient.objects.create(user_id=user_id, cedula_encrypted=encrypt_cedula("0102030405"), blood_type="O+")
