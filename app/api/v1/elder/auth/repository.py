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

def get_primary_relationship(db: Session, elder_id: int):
    q = text("""SELECT TOP 1 RelationshipID, ElderID, CaregiverID FROM CareRelationships
        WHERE ElderID = :elder_id AND IsPrimary = 1""")
    r = db.execute(q, {"elder_id": elder_id}).mappings().first()
    return r 
def update_user_timezone_and_lastlogin(db, user_id: int, timezone_name: str, timezone_offset: str):
    tz = f"{timezone_name} {timezone_offset}"  # ex: "IST +05:30"
    db.execute(
        text("""UPDATE Users SET LastLogin = GETDATE(), Timezone = :tz WHERE UserID = :uid"""),
        {"uid": user_id, "tz": tz}
    )