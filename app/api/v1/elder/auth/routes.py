
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.core.database import get_db
from .repository import login_elder, upsert_user_device
from .schemas import  ElderLogin, ElderLoginResponse

from sqlalchemy import text

router = APIRouter(prefix="/elder", tags=["Elder login"])

@router.post("/login", response_model=ElderLoginResponse)
def login(data: ElderLogin, db: Session = Depends(get_db)):

    login = login_elder(db, data.email)

    if not login:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = login["user"]

    if not verify_password(data.password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password. Try again")

    try:
        db.execute(
            text("""INSERT INTO UserLogins (UserID, RoleID, LoginTime) VALUES (:uid, :rid, GETDATE())"""),
            {"uid": user["UserID"], "rid": user["RoleID"]}
        )

        db.execute(
            text("""UPDATE Users SET LastLogin = GETDATE() WHERE UserID = :uid"""),
            {"uid": user["UserID"]}
        )

        if data.fcm_token:
            upsert_user_device(
                db,
                user["UserID"],
                data.fcm_token,
                data.app_type,
                data.device_model
            )

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "user_id": user["UserID"],
        "full_name": user["FullName"],
        "email": user["Email"],
        "phone": user["Phone"],
        "address": user["Address"],
        "date_of_birth": user["DateOfBirth"],
        "gender": user["Gender"],
        "created_at": user["CreatedAt"]
    }