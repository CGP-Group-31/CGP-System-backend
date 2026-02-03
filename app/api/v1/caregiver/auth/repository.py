# app/api/v1/caregiver/repository.py

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError, SQLAlchemyError



ROLE_CAREGIVER = 4

def create_caregiver(db, data):
    query = text("""
        INSERT INTO Users
        (RoleID, FullName, Email, Phone, PasswordHash,
         DateOfBirth, Gender, IsActive, CreatedAt, LastLogin, address)
        OUTPUT INSERTED.UserID
        VALUES
        (:role_id, :full_name, :email, :phone, :password,
         :dob, :gender, 1, GETDATE(), GETDATE(), :address)""")

    result = db.execute(
        query,
        {
            "role_id": ROLE_CAREGIVER,
            "full_name": data.full_name,
            "email": data.email,
            "phone": data.phone,
            "password": hash_password(data.password), 
            "dob": data.date_of_birth,
            "gender": data.gender,
            "address": data.address
        }
    )
  
    return result.scalar()


def login_caregiver(db, email: str):

    query = text("""
        SELECT UserID, RoleID, FullName, Email, Phone, Address, PasswordHash, DateOfBirth, Gender, CreatedAt 
        FROM Users
        WHERE Email = :email AND RoleID = :role_id AND IsActive = 1""")

    result = db.execute(query, {
        "email": email,
        "role_id": ROLE_CAREGIVER
    })

    return result.mappings().first()


def login(db: Session, email: str, password: str):
    user = login_caregiver(db, email)
    if not user:
        return None

    if not verify_password(password, user["PasswordHash"]):
        return None
    db.execute(
        text("""
            INSERT INTO UserLogins (UserID, RoleID, LoginTime)
            VALUES (:user_id, :role_id, GETDATE())
        """),
        {
            "user_id": user["UserID"],
            "role_id": user["RoleID"]
        }
    )

    db.execute(
        text("""
            UPDATE Users
            SET LastLogin = GETDATE()
            WHERE UserID = :user_id
        """),
        {"user_id": user["UserID"]}
    )

    return user
