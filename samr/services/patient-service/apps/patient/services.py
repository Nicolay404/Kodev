from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def encrypt_cedula(value: str) -> bytes:
    return Fernet(settings.PATIENT_DATA_KEY.encode()).encrypt(value.encode())


def decrypt_cedula(value: bytes) -> str:
    try:
        return Fernet(settings.PATIENT_DATA_KEY.encode()).decrypt(bytes(value)).decode()
    except InvalidToken as exc:
        raise ValueError("No fue posible descifrar la cédula") from exc
