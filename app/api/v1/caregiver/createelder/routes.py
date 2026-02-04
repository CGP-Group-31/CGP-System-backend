import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password
from app.core.database import get_db
from .repository import create_elder, create_relationship
from .schemas import ElderCreate, ElderCreateResponse, ElderRelationship, ElderRelationshipResponse

router = APIRouter(prefix="/elder", tags=["Elder Create"])

@router.post("/register", response_model=ElderCreateResponse, status_code=status.HTTP_201_CREATED)
def register_elder(data: ElderCreate, db: Session = Depends(get_db)):
    try:
        user_id = create_elder(db, data)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/elder-relationship",
    response_model=ElderRelationshipResponse,
    status_code=status.HTTP_201_CREATED
)
def create_elder_relationship(
    data: ElderRelationship,
    db: Session = Depends(get_db)
):
    relationship_id = create_relationship(db, data)
    return {"relationship_id": relationship_id}

# @router.post("/login")
# def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

#     user = login_elder(db, data.username)

#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     if not verify_password(data.password, user["PasswordHash"]):
#         raise HTTPException(status_code=401, detail="Invalid email or password")
#     return {
#         "user_id": user["UserID"],
#         "full_name": user["FullName"],
#         "email": user["Email"],
#         "phone": user["Phone"],
#         "address": user["Address"],
#         "date_of_birth": user["DateOfBirth"],
#         "gender": user["Gender"],
#         "created_at": user["CreatedAt"]
#     }