import pytest
from rest_framework.test import APIClient
from apps.patient.models import Patient
import jwt
import datetime
from django.conf import settings
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

@pytest.fixture(scope="session")
def rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()
    return private_key, public_key

@pytest.fixture(autouse=True)
def mock_jwt_keys(monkeypatch, tmp_path, rsa_keys):
    private_key, public_key = rsa_keys
    
    pub_path = tmp_path / "public.pem"
    with open(pub_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        
    monkeypatch.setattr(settings, 'JWT_PUBLIC_KEY_PATH', str(pub_path))

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def valid_jwt(rsa_keys):
    private_key, _ = rsa_keys
    payload = {
        'usuario_id': 100,
        'email': 'test@patient.com',
        'rol': 'patient',
        'type': 'access',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    }
    return jwt.encode(payload, private_key, algorithm='RS256')

@pytest.fixture
def patient():
    return Patient.objects.create(
        user_id=100,
        full_name='Test Patient',
        age=30,
        gender='Male'
    )
