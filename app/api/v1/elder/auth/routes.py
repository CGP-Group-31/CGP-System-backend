
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.core.database import get_db
from .repository import login_elder, upsert_user_device, get_primary_relationship,  update_user_timezone_and_lastlogin

from .schemas import  ElderLogin, ElderLoginResponse

from sqlalchemy import text

router = APIRouter(prefix="/elder", tags=["Elder login"])

@router.post("/login", response_model=ElderLoginResponse)
def login(data: ElderLogin, db: Session = Depends(get_db)):

    login_result = login_elder(db, data.email)
    if not login_result:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = login_result["user"]

    if not verify_password(data.password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password. Try again")

    try:
        update_user_timezone_and_lastlogin(
            db=db,
            user_id=user["UserID"],
            timezone_name=data.timezone_name,
            timezone_offset=data.timezone_offset
        )

        # db.execute(
        #     text("""INSERT INTO UserLogins (UserID, RoleID, LoginTime) VALUES (:uid, :rid, GETDATE())"""),
        #     {"uid": user["UserID"], "rid": user["RoleID"]}
        # )

        if data.fcm_token:
            upsert_user_device(
                db,
                user["UserID"],
                data.fcm_token,
                data.app_type,
                data.device_model or "unknown"
            )
        relationship = get_primary_relationship(db, elder_id=user["UserID"])

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "user_id": user["UserID"],
        "role_id": user["RoleID"],
        "full_name": user["FullName"],
        "email": user["Email"],
        "phone": user["Phone"],
        "address": user["Address"],
        "date_of_birth": user["DateOfBirth"],
        "gender": user["Gender"],
        "created_at": user["CreatedAt"],
        "relationshipid": relationship["RelationshipID"],
        "caregiverid": relationship["CaregiverID"],
    }