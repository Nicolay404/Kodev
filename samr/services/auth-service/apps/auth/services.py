import jwt
import datetime
from django.conf import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def get_private_key():
    try:
        with open(settings.JWT_PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró la clave privada en la ruta configurada: {settings.JWT_PRIVATE_KEY_PATH}")

def get_public_key():
    try:
        with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        return public_key
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró la clave pública en la ruta configurada: {settings.JWT_PUBLIC_KEY_PATH}")

def generar_jwt_pair(user):
    private_key = get_private_key()
    
    # Access Token (expira en 15 mins)
    access_payload = {
        'usuario_id': user.id,
        'email': user.email,
        'rol': user.rol,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15),
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'type': 'access'
    }
    access_token = jwt.encode(access_payload, private_key, algorithm='RS256')
    
    # Refresh Token (expira en 7 días)
    refresh_payload = {
        'usuario_id': user.id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, private_key, algorithm='RS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

def verify_jwt(token):
    public_key = get_public_key()
    try:
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expirado")
    except jwt.InvalidTokenError:
        raise Exception("Token inválido")
