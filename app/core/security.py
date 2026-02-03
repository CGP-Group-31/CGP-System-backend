# app/core/security.py

from passlib.context import CryptContext

import bcrypt

def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 bytes)")

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )
    return hashed.decode("utf-8")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against bcrypt hash
    """
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")

    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    return bcrypt.checkpw(plain_password, hashed_password)

    try:
        is_valid = verify_password(data.password, user["PasswordHash"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid email or password")
