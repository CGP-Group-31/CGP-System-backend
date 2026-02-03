
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password
from app.core.database import get_db
from .repository import create_caregiver, login

from .schemas import (
    CaregiverCreate,
    CaregiverCreateResponse,
    CaregiverLogin,
    CaregiverLoginResponse
)
from .repository import create_caregiver, login_caregiver
router = APIRouter(prefix="/auth", tags=["Caregivers"])
router = APIRouter(prefix="/auth", tags=["Caregiver Auth"])

@router.post(
    "/register",
    response_model=CaregiverCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def register_caregiver(
    data: CaregiverCreate,
    db: Session = Depends(get_db)
):
    try:
        user_id = create_caregiver(db, data)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(data: CaregiverLogin, db: Session = Depends(get_db)):

    user = login_caregiver(db, data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(data.password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
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
