import datetime
import hashlib
import hmac
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


def generar_password_reset_token(user):
    now = datetime.datetime.now(datetime.timezone.utc)
    private_key = _load_key(settings.JWT_PRIVATE_KEY_PATH, private=True)
    payload = {
        "usuario_id": str(user.id),
        "email": user.email,
        "pwd": hashlib.sha256(user.password.encode("utf-8")).hexdigest(),
        "type": "password_reset",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=15),
        "jti": str(uuid.uuid4()),
        "iss": "samr-auth-service",
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


def verify_password_reset_token(token, user):
    payload = verify_jwt(token)
    expected = hashlib.sha256(user.password.encode("utf-8")).hexdigest()
    if payload.get("type") != "password_reset" or str(payload.get("usuario_id")) != str(user.id):
        raise TokenError("Token de recuperación inválido")
    if not hmac.compare_digest(str(payload.get("pwd", "")), expected):
        raise TokenError("Token de recuperación ya utilizado")
    return payload
