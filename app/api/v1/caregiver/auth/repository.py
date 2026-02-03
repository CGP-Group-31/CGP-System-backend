# app/api/v1/caregiver/repository.py

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password

ROLE_CAREGIVER = 4

def create_caregiver(db, data):
    query = text("""
        INSERT INTO Users
        (RoleID, FullName, Email, Phone, PasswordHash,
         DateOfBirth, Gender, IsActive, CreatedAt, LastLogin)
        OUTPUT INSERTED.UserID
        VALUES
        (:role_id, :full_name, :email, :phone, :password,
         :dob, :gender, 1, GETDATE(), GETDATE())""")

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
        }
    )

    return result.scalar()
