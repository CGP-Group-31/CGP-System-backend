import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password
from app.core.database import get_db
from .repository import login_elder
from .schemas import  ElderLogin, ElderLoginResponse
# ElderCreate, ElderCreateResponse, ElderRelationship, ElderRelationshipResponse,
router = APIRouter(prefix="/elder", tags=["Elder login"])

# not sure / work
@router.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = login_elder(db, data.username)

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