import datetime
import uuid

import jwt
from cryptography.hazmat.primitives import serialization
from django.conf import settings


class TokenError(Exception):
    pass


def _load_key(path, private=False):
    try:
        with open(path, "rb") as key_file:
            content = key_file.read()
    except FileNotFoundError as exc:
        raise TokenError(f"No se encontró la clave JWT en {path}") from exc
    if private:
        return serialization.load_pem_private_key(content, password=None)
    return serialization.load_pem_public_key(content)


def generar_jwt_pair(user):
    now = datetime.datetime.now(datetime.timezone.utc)
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH, private=True)
    common = {
        "usuario_id": str(user.id),
        "iat": now,
        "jti": str(uuid.uuid4()),
        "iss": "samr-auth-service",
    }
    access = {
        **common,
        "email": user.email,
        "rol": user.role,
        "type": "access",
        "exp": now + datetime.timedelta(minutes=15),
    }
    refresh = {
        **common,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
        "exp": now + datetime.timedelta(days=7),
    }
    return {
        "access_token": jwt.encode(access, private_key, algorithm="RS256"),
        "refresh_token": jwt.encode(refresh, private_key, algorithm="RS256"),
    }


def verify_jwt(token):
    try:
        return jwt.decode(
            token,
            _load_key(settings.JWT_PUBLIC_KEY_PATH),
            algorithms=["RS256"],
            issuer="samr-auth-service",
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token expirado") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Token inválido") from exc
