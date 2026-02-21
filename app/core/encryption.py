from cryptography.fernet import Fernet
import os

SECRET_KEY = os.getenv("ENCRYPTION_KEY")

if not SECRET_KEY:
 
    SECRET_KEY = Fernet.generate_key().decode()
    

fernet = Fernet(SECRET_KEY.encode())


def encrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return fernet.encrypt(value.encode()).decode()


def decrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return fernet.decrypt(value.encode()).decode()