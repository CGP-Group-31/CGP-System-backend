from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date, time, datetime
import re

NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z\s\.\-']{1,99}$")


class AppointmentCreate(BaseModel):
    elder_id: int = Field(...,gt=0)
    doctor_name: str = Field(..., min_length=3, max_length=100)
    title: str = Field(..., min_length=2, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=200)
    appointment_date: date
    appointment_time: time

    @field_validator("doctor_name")
    @classmethod 
    def validate_doctor_name(cls, v:str):
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Invalid doctor name")
        return v



class AppointmentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    appointment_id: int = Field(alias="AppointmentID")
    elder_id: int = Field(alias="ElderID")
    doctor_name: str = Field(alias="DoctorName")
    title: str = Field(alias="Title")
    location: Optional[str] = Field(alias="Location")
    notes:Optional[str] = Field(alias="Notes")
    appointment_date: date = Field(alias="AppointmentDate")
    appointment_time: Optional[time] = Field(alias="AppointmentTime")  

    


class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str]  = Field(None, min_length=2, max_length=100)
    title: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    notes: Optional[str] = Field(None, min_length=2, max_length=100)
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None  

    @field_validator("doctor_name")
    @classmethod 
    def validate_doctor_name(cls, v:Optional[str]):
        if v is None:
            return v
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Invalid doctor name")
        return v

    