import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app.core.security import verify_password
from app.core.database import get_db
from .repository import create_elder, create_relationship, add_elder_records, all_doctors
from .schemas import  ElderProfile , ElderRegisterRequest, ElderRegisterResponse,ElderProfileResponse, DoctorResponse
from .schemas import EmergencyContactCreate, EmergencyContactResponse, DoctorSearchRequest, DoctorResponse
from .repository import create_emergency_contact, get_emergency_contacts, search_doctors


# ElderCreate, ElderCreateResponse, ElderRelationship, ElderRelationshipResponse,
router = APIRouter(prefix="/elder-create", tags=["Elder Create"])

# @router.post("/register", response_model=ElderCreateResponse, status_code=status.HTTP_201_CREATED)
# def register_elder(data: ElderCreate, db: Session = Depends(get_db)):
#     try:
#         user_id = create_elder(db, data)
#         return {"user_id": user_id}
#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=str(e)
#         )


# @router.post(
#     "/elder-relationship",
#     response_model=ElderRelationshipResponse,
#     status_code=status.HTTP_201_CREATED
# )
# def create_elder_relationship(
#     data: ElderRelationship,
#     db: Session = Depends(get_db)
# ):
#     relationship_id = create_relationship(db, data)
#     return {"relationship_id": relationship_id}
@router.post(
    "/register",
    response_model=ElderRegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register_elder(
    data: ElderRegisterRequest,
    db: Session = Depends(get_db)
):
    try:
        # start transaction
        elder_id = create_elder(db, data)

        relationship_id = create_relationship(
            db=db,
            elder_id=elder_id,
            caregiver_id=data.caregiver_id,
            relationship_type=data.relationship_type,
            is_primary=data.is_primary
        )

        db.commit()

        return {
            "user_id": elder_id,
            "relationship_id": relationship_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to register elder"
        )

@router.post(
    "/elder-profile",
    response_model=ElderProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def add_elder_profile(
    data: ElderProfile,
    db: Session = Depends(get_db)
):
    try:
        profile_id = add_elder_records(db, data.elder_id, data)
        db.commit()
        return {"profile_id": profile_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to create elder profile"
        )


@router.get("/all-doctors",response_model=list[DoctorResponse], status_code=status.HTTP_200_OK)
def get_all_doctors(db: Session = Depends(get_db)):
    doctors = all_doctors(db)

    if not doctors:
        raise HTTPException(
            status_code=404,
            detail="No doctors found"
        )

    return doctors


@router.post("/emergency-contacts", status_code=201)
def add_emergency_contact(
    payload: EmergencyContactCreate,
    db: Session = Depends(get_db)
):
    create_emergency_contact(db, payload)
    return {"message": "Emergency contact added successfully"}


@router.get(
    "/get-emergency-contacts/{elder_id}",
    response_model=List[EmergencyContactResponse]
)
def list_emergency_contacts(
    elder_id: int,
    db: Session = Depends(get_db)
):
    contacts = get_emergency_contacts(db, elder_id)
    return contacts

@router.post("/search-doctors",
             response_model=list[DoctorResponse],
             status_code=status.HTTP_200_OK)
def search_doctors_api(
    data: DoctorSearchRequest,
    db: Session = Depends(get_db)
):

    # If both fields are empty
    if not data.doctor_name and not data.hospital:
        raise HTTPException(
            status_code=400,
            detail="Please provide doctor_name or hospital for searching"
        )

    doctors = search_doctors(
        db,
        doctor_name=data.doctor_name,
        hospital=data.hospital
    )

    if not doctors:
        raise HTTPException(
            status_code=404,
            detail="No doctors found"
        )

    return doctors