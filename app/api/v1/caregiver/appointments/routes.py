from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from .repository import(get_all_appointments, update_appointment, get_one_appointment, delete_appointment, create_appointment)
from typing import List


router= APIRouter(prefix="/appointments", tags=["Doctor Appointment"])

@router.post("/")
def create_appointments_for_elder(data: AppointmentCreate, db: Session= Depends(get_db)):
        create_appointment(db, data)
        return {
            "message": "Appointment created successfully"}


@router.get("/elder/{elder_id}", response_model=List[AppointmentResponse])
def get_all_appointments_of_elder(elder_id: int, db: Session = Depends(get_db)):
    return get_all_appointments(db, elder_id)

   

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_one_appointment_of_elder(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_one_appointment(db, appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=dict)
def update_appointment_of_elder(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):
    updated = update_appointment(db,appointment_id,data) 

    if not updated:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment updated successfully"}


@router.delete("/{appointment_id}", response_model=dict)
def delete_appointment_for_elder(appointment_id: int, db: Session = Depends(get_db)):
    deleted = delete_appointment(db, appointment_id )
    if not deleted:
         raise HTTPException(status_code=404, detail="Appointment not found")
    return{"message":"Appointment deleted successfully"}