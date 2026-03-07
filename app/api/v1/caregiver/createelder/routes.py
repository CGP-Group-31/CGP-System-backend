import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app.core.security import verify_password
from app.core.database import get_db
from .repository import create_elder, create_relationship, add_elder_records, all_doctors, update_elder_preferred_doctor
from .schemas import  ElderProfile , ElderRegisterRequest, ElderRegisterResponse,ElderProfileResponse, ElderProfileUpdate, ElderDoctorUpdate
from .schemas import EmergencyContactCreate, EmergencyContactResponse, DoctorSearchRequest, DoctorResponse,  MessageResponse
from .repository import create_emergency_contact, get_emergency_contacts, search_doctors, update_elder_profile

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

@router.post("/elder-profile",
    response_model=ElderProfileResponse,status_code=status.HTTP_201_CREATED)
def add_elder_profile(
    data: ElderProfile,
    db: Session = Depends(get_db)):
    profile_id, error = add_elder_records(db, data.elder_id, data)

    if error:
        raise HTTPException(status_code=400, detail=error)
    db.commit()
    return {"profile_id": profile_id}

@router.get("/all-doctors",response_model=list[DoctorResponse], status_code=status.HTTP_200_OK)
def get_all_doctors(db: Session = Depends(get_db)):
    doctors = all_doctors(db)

    if not doctors:
        raise HTTPException(
            status_code=404,
            detail="No doctors found"
        )

    return doctors

@router.post("/emergency-contacts",response_model=MessageResponse,
             status_code=status.HTTP_201_CREATED)
def add_emergency_contact(
    payload: EmergencyContactCreate,
    db: Session = Depends(get_db)
):
    contact_id, err = create_emergency_contact(db, payload)

    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    return {"message": f"Emergency contact added successfully"}

@router.get(
    "/get-emergency-contacts/{elder_id}",
    response_model=List[EmergencyContactResponse],
    status_code=status.HTTP_200_OK
)
def list_emergency_contacts(
    elder_id: int,
    db: Session = Depends(get_db)
):
    if elder_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="elder_id must be greater than 0")

    contacts, err = get_emergency_contacts(db, elder_id)

    if err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err)
    return contacts or []
@router.post("/search-doctors",
             response_model=list[DoctorResponse],
             status_code=status.HTTP_200_OK)
def search_doctors_api(
    data: DoctorSearchRequest,
    db: Session = Depends(get_db)):

    if not data.doctor_name and not data.hospital:
        raise HTTPException(
            status_code=400,
            detail="Please provide doctor_name or hospital for searching")

    doctors = search_doctors(
        db,
        doctor_name=data.doctor_name,
        hospital=data.hospital)

    if not doctors:
        raise HTTPException(
            status_code=404,
            detail="No doctors found")

    return doctors

@router.put("/elder-profile-update/{elder_id}", status_code=200)
def update_elder_profile_api(
    elder_id: int,
    payload: ElderProfileUpdate,
    db: Session = Depends(get_db)
):
    success, error = update_elder_profile(db, elder_id, payload)

    if error:
        raise HTTPException(status_code=400, detail=error)

    return {"message": "Elder profile updated successfully"}

@router.put("/elder-profile-update-doctor/{elder_id}", status_code=200)
def update_elder_preferred_doctor_api(
    elder_id: int,
    payload: ElderDoctorUpdate,
    db: Session = Depends(get_db)
):
    success, error = update_elder_preferred_doctor(
        db,
        elder_id,
        payload.preferred_doctor_id
    )

    if error:
        raise HTTPException(status_code=400, detail=error)

    return {"message": "Preferred doctor updated successfully"}