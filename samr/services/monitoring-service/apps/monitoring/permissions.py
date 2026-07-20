from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
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
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expirado")
    except jwt.InvalidTokenError as e:
        raise AuthenticationFailed(f"Token inválido: {str(e)}")

class DummyUser:
    def __init__(self, id, email, rol):
        self.id = id
        self.email = email
        self.rol = rol
    
    @property
    def is_authenticated(self):
        return True

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
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

class DeviceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate_header(self, request):
        return 'X-Device-Token'

    def authenticate(self, request):
        token = request.headers.get('X-Device-Token')
        if not token:
            return None
            
        # Para propósitos de este servicio base, permitimos cualquier token de dispositivo que empiece con "DEV-"
        if not token.startswith('DEV-'):
            raise AuthenticationFailed('Device token inválido')
            
        user = DummyUser(id=0, email='device@iot', rol='device')
        return (user, token)
