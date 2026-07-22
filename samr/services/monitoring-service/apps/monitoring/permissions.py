from cryptography.hazmat.primitives import serialization
from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
import jwt


def verify_jwt(token):
    try:
        with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as key_file:
            key = serialization.load_pem_public_key(key_file.read())
        return jwt.decode(token, key, algorithms=["RS256"], issuer="samr-auth-service")
    except (OSError, jwt.InvalidTokenError) as exc:
        raise AuthenticationFailed("Token inválido") from exc


class Principal:
    def __init__(self, id, email, rol): self.id, self.email, self.rol = id, email, rol
    @property
    def is_authenticated(self): return True


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request): return "Bearer"
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "): return None
        payload = verify_jwt(header[7:])
        if payload.get("type") != "access": raise AuthenticationFailed("Se requiere access token")
        return Principal(payload["usuario_id"], payload.get("email", ""), payload["rol"]), header[7:]


class DeviceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request): return "X-Service-Token"
    def authenticate(self, request):
        token = request.headers.get("X-Service-Token")
        if not token: return None
        if token != settings.MVP_DEVICE_SERVICE_TOKEN: raise AuthenticationFailed("Token de dispositivo inválido")
        return Principal("device", "device@iot", "device"), token
