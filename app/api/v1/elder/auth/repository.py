from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


ROLE_ELDER = 5

def login_elder(db, email: str):

    query = text("""
        SELECT UserID, RoleID, FullName, Email, Phone, Address, PasswordHash, DateOfBirth, Gender, CreatedAt 
        FROM Users
        WHERE Email = :email AND RoleID = :role_id AND IsActive = 1""")

    result = db.execute(query, {
        "email": email,
        "role_id": ROLE_ELDER
    })

    return result.mappings().first()
