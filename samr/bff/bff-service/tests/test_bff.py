import pytest
import datetime
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app, JWT_PUBLIC_KEY_PATH

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
    monkeypatch.setattr('main.JWT_PUBLIC_KEY_PATH', str(pub_path))

def _create_jwt(private_key, rol, user_id=100):
    payload = {
        'usuario_id': user_id,
        'email': f'{rol}@test.com',
        'rol': rol,
        'type': 'access',
        'iss': 'samr-auth-service',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    }
    return jwt.encode(payload, private_key, algorithm='RS256')

@pytest.fixture
def auth_jwt_patient(rsa_keys):
    return _create_jwt(rsa_keys[0], 'patient')

def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_dashboard_patient(auth_jwt_patient):
    
    # Mocking httpx response
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
        def json(self):
            return self.json_data

    with TestClient(app) as client:
        with patch('main.http_client.get', return_value=MockResponse({"mock": "data"}, 200)) as mock_get:
            response = client.get("/dashboard/", headers={"Authorization": f"Bearer {auth_jwt_patient}"})
    assert response.status_code == 200
    assert set(response.json()) == {'role', 'patient', 'solicitudes', 'monitoring', 'atencion', 'emergencias', 'teleconsultas', 'notificaciones'}
    assert response.json()['role'] == 'patient'
    assert response.json()['patient'] == {"mock": "data"}
