# app/core/encryption.py

from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

try:
    fernet = Fernet(settings.encryption_key.encode())
except Exception:
    raise RuntimeError("Invalid ENCRYPTION_KEY format.")


def encrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return fernet.encrypt(value.encode()).decode()


def decrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return fernet.decrypt(value.encode()).decode()
    except InvalidToken:
        raise RuntimeError("Invalid encryption token.")