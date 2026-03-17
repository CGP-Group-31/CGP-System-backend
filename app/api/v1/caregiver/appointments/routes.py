from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from typing import List

from .repository import (
    update_appointment,
    delete_appointment,
    create_appointment,
    upcoming_appointments,
    upsert_appointment_reminders,
    delete_appointment_reminders
)

router= APIRouter(prefix="/appointments", tags=["Doctor Appointment"])

@router.post("/")
def create_appointments_for_elder(data: AppointmentCreate, db: Session = Depends(get_db)):
    appointment_id = create_appointment(db, data)
    
    if not appointment_id:
        raise HTTPException(status_code=400, detail="Failed to create appointment")
    
    upsert_appointment_reminders(db, appointment_id)
    db.commit()
    
    return {
        "message": "Appointment created successfully",
        "appointment_id": appointment_id
    }

    #  create 24H + 6H reminders
    upsert_appointment_reminders(db, appointment_id)

    db.commit()
    return {"message": "Appointment created successfully", "appointment_id": appointment_id}


@router.get("/elder/{elder_id}/upcoming-7-days", response_model=List[AppointmentResponse])
def get_appointment_of_7(elder_id: int, db: Session = Depends(get_db)):
    appointment = upcoming_appointments(db, elder_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Upcoming appointments not found")

    return appointment


@router.patch("/{appointment_id}", response_model=dict)
def update_appointment_of_elder(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):

    updated = update_appointment(db, appointment_id, data)

    if updated == "no_fields":
        raise HTTPException(status_code=400, detail="No fields provided")

    if updated == "not_found":
        raise HTTPException(status_code=404, detail="Appointment not found")
    upsert_appointment_reminders(db, appointment_id)

    db.commit()
    return {"message": "Appointment updated successfully"}



@router.delete("/{appointment_id}", response_model=dict)
def delete_appointment_for_elder(appointment_id: int, db: Session = Depends(get_db)):
    #  delete reminders first (foreign key safe)
    delete_appointment_reminders(db, appointment_id)

    deleted = delete_appointment(db, appointment_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.commit()
    return {"message": "Appointment deleted successfully"}
