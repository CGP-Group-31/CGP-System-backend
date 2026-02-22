from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .schemas import ElderLogin, ElderLoginResponse

ROLE_ELDER = 5

def upsert_user_device(
    db: Session,
    user_id: int,
    fcm_token: str,
    app_type: str,
    device_model: str
):
    result = db.execute(
        text("""UPDATE UserDevices SET  FCMToken = :fcm_token, app_type = :app_type, Device_model = :device_model,
                LastUpdated = GETDATE() WHERE UserID = :user_id"""),
        {
            "user_id": user_id,
            "fcm_token": fcm_token,
            "app_type": app_type,
            "device_model": device_model
        }
    )

    if result.rowcount == 0:
        db.execute(
            text("""INSERT INTO UserDevices (UserID, FCMToken, app_type, Device_model, LastUpdated)
                VALUES
                (:user_id, :fcm_token, :app_type, :device_model, GETDATE())"""),
            {
                "user_id": user_id,
                "fcm_token": fcm_token,
                "app_type": app_type,
                "device_model": device_model
            }
        )

def login_elder(db, email: str):

    query = text("""
        SELECT UserID, RoleID, FullName, Email, Phone, Address, PasswordHash, DateOfBirth, Gender, CreatedAt 
        FROM Users
        WHERE Email = :email AND RoleID = :role_id AND IsActive = 1""")

    result = db.execute(query, {
        "email": email,
        "role_id": ROLE_ELDER
    })

    user= result.mappings().first()
    if not user:
        return None
    return{"user":user}
