from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
import jwt
from django.conf import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def verify_jwt(token):
    try:
        with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
    except FileNotFoundError:
        raise AuthenticationFailed(f"Llave pública no encontrada en {settings.JWT_PUBLIC_KEY_PATH}")
        
    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'], issuer="samr-auth-service")
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expirado")
    except jwt.InvalidTokenError as e:
        raise AuthenticationFailed(f"Token inválido: {str(e)}")

class DummyUser:
    def __init__(self, id, email, rol, is_m2m=False):
        self.id = id
        self.email = email
        self.rol = rol
        self.is_m2m = is_m2m
    
    @property
    def is_authenticated(self):
        return True

class DualAuthentication(authentication.BaseAuthentication):
    """
    Soporta X-Service-Token (para M2M) y JWT (para usuarios).
    """
    def authenticate(self, request):
        # 1. Probar autenticación M2M
        service_token = request.headers.get('X-Service-Token')
        if service_token:
            if service_token == settings.SERVICE_TOKEN:
                user = DummyUser(id=0, email='service@samr.local', rol='service', is_m2m=True)
                return (user, service_token)
            else:
                raise AuthenticationFailed('Token de servicio inválido')
                
        # 2. Probar autenticación JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        payload = verify_jwt(token)
        
        if payload.get('type') != 'access':
            raise AuthenticationFailed('Tipo de token inválido. Se requiere un access token.')
            
        user = DummyUser(
            id=payload['usuario_id'],
            email=payload['email'],
            rol=payload['rol']
        )
        return (user, token)

class IsSystemAdmin(BasePermission):
    """
    Requiere rol 'system_admin'
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and not getattr(user, 'is_m2m', False) and getattr(user, 'rol', None) == 'system_admin')

class IsServiceOrAdmin(BasePermission):
    """
    Permite acceso M2M o Admin.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'is_m2m', False):
            return True
        return getattr(user, 'rol', None) == 'system_admin'
