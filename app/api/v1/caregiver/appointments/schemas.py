from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class AppointmentCreate(BaseModel):
    elder_id: int
    doctor_name: str
    title: str
    location: str
    notes: Optional[str] = None
    appointment_date: date
    appointment_time: time  #24 format?



class AppointmentResponse(BaseModel):
    ElderID: int
    DoctorName: str
    Title: str
    Location: str
    Notes: Optional[str] = None
    AppointmentDate: date
    AppointmentTime: time  #24 format?
    


class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str]=None
    title: Optional[str] = None
    location: Optional[str]= None
    notes: Optional[str] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None  #24 format?
    recorded_at:  Optional[datetime] = None



