# app/api/v1/caregiver/auth/repository.py

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .schemas import CaregiverCreate

# ROLE_CAREGIVER = 4


def upsert_user_device(
    db: Session,
    user_id: int,
    fcm_token: str,
    app_type: str,
    device_model: str
):
    result = db.execute(
        text("""UPDATE UserDevices SET 
                FCMToken = :fcm_token,
                app_type = :app_type,
                Device_model = :device_model,
                LastUpdated = GETDATE() WHERE UserID = :user_id"""),
        {
            "user_id": user_id,
            "fcm_token": fcm_token,
            "app_type": app_type,
            "device_model": device_model
        }
    )

    # If no row updated → insert
    if result.rowcount == 0:
        db.execute(
            text("""INSERT INTO UserDevices
                (UserID, FCMToken, app_type, Device_model, LastUpdated) VALUES
                 (:user_id, :fcm_token, :app_type, :device_model, GETDATE())"""),
            {
                "user_id": user_id,
                "fcm_token": fcm_token,
                "app_type": app_type,
                "device_model": device_model
            }
        )



def create_caregiver(db: Session, data: CaregiverCreate):
    result = db.execute(
        text("""INSERT INTO Users (RoleID, FullName, Email, Phone, PasswordHash,
             DateOfBirth, Gender, IsActive, CreatedAt, LastLogin, Address)
            OUTPUT INSERTED.UserID
            VALUES
            (4, :full_name, :email, :phone, :password,:dob, :gender, 1, GETDATE(), GETDATE(), :address)"""),
        {
            "full_name": data.full_name,
            "email": data.email,
            "phone": data.phone,
            "password": hash_password(data.password),
            "dob": data.date_of_birth,
            "gender": data.gender,
            "address": data.address
        }
    )

    user_id = result.scalar()

    if data.fcm_token:
        upsert_user_device(
            db,
            user_id,
            data.fcm_token,
            data.app_type,
            data.device_model
        )

    return user_id


def login_caregiver(db: Session, email: str):
    result = db.execute(
        text("""SELECT UserID, RoleID, FullName, Email, Phone, Address, PasswordHash, DateOfBirth, Gender, CreatedAt
            FROM Users WHERE Email = :email AND RoleID = 4 AND IsActive = 1"""),
        {"email": email}
    )

    return result.mappings().first()

