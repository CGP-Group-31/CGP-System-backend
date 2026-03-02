# app/api/v1/caregiver/auth/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.security import verify_password
from app.core.database import get_db

from .repository import create_caregiver, login_caregiver, upsert_user_device
from .schemas import CaregiverCreate, CaregiverLogin, CaregiverLoginResponse

router = APIRouter(prefix="/auth", tags=["Caregiver Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_caregiver(data: CaregiverCreate, db: Session = Depends(get_db)):
    try:
        user_id = create_caregiver(db, data)
        db.commit()
        return {"user_id": user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=CaregiverLoginResponse)
def login(data: CaregiverLogin, db: Session = Depends(get_db)):

    login_data = login_caregiver(db, data.email)

    if not login_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = login_data["user"]

    if not verify_password(data.password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

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
        "role_id": user["RoleID"],
        "full_name": user["FullName"],
        "email": user["Email"],
        "phone": user["Phone"],
        "address": user["Address"],
        "date_of_birth": user["DateOfBirth"],
        "gender": user["Gender"],
        "created_at": user["CreatedAt"],
        "elder_id": login_data["elder_id"],
        "relationship_id": login_data["relationship_id"],
    }