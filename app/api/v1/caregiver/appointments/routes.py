from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from .schemas import AppointmentCreate, AppointmentResponse, AppointmentUpdate
from .repository import(get_all_appointments, update_appointment, get_one_appointment, delete_appointment, create_appointment, upcoming_appointments)
from typing import List


router= APIRouter(prefix="/appointments", tags=["Doctor Appointment"])

@router.post("/")
def create_appointments_for_elder(data: AppointmentCreate, db: Session= Depends(get_db)):
        create = create_appointment(db, data)

        if not create:
            raise HTTPException(status_code=404, detail="Failed to create appointment")
        db.commit()
        return {"message": "Appointment created successfully"}



@router.get("/elder/{elder_id}", response_model=List[AppointmentResponse])
def get_all_appointments_of_elder(elder_id: int, db: Session = Depends(get_db)):
    appointments = get_all_appointments(db, elder_id)

    if not appointments:
        raise HTTPException(status_code=404, detail="Appointments not found")
    return appointments

   

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_one_appointment_of_elder(appointment_id: int, db: Session = Depends(get_db)):
    appointment = get_one_appointment(db, appointment_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=dict)
def update_appointment_of_elder(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db)):
    updated = update_appointment(db,appointment_id,data) 

    if updated == "no_fields":
        raise HTTPException(status_code=400, detail="No fields provided")
    if updated == "not_found":
        raise HTTPException(status_code=404, detail="Caregiver not found")

    db.commit()
    return {"message": "Appointment updated successfully"}


@router.delete("/{appointment_id}", response_model=dict)
def delete_appointment_for_elder(appointment_id: int, db: Session = Depends(get_db)):
    deleted = delete_appointment(db, appointment_id )
    if not deleted:
         raise HTTPException(status_code=404, detail="Appointment not found")
    return{"message":"Appointment deleted successfully"}


@router.get("/elder/{elder_id}/upcoming-7-days", response_model=AppointmentResponse)
def get_appointment_of_7(elder_id: int, db: Session = Depends(get_db)):
    appointment = upcoming_appointments(db, elder_id)

    if not appointment:
        raise HTTPException(status_code=404, detail="Upcoming appointments not found")
    return appointment
