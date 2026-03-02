from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import date, time, datetime
import re

NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z\s\.\-']{1,99}")
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")  # 24h HH:MM

def normalize_hhmm(v: str) -> str:
    v=v.strip()
    if not TIME_RE.match(v):
        raise ValueError("Invalid time format. Use format: HH:MM 24h")
    hh, mm = v.split(":")
    return time(hour=int(hh), minute=int(mm))




class AppointmentCreate(BaseModel):
    elder_id: int = Field(...,gt=0)
    doctor_name: str = Field(..., min_length=3, max_length=100)
    title: str = Field(..., min_length=2, max_length=100)
    location: Optional[str] = Field(..., min_length=2, max_length=100)
    notes: Optional[str] = Field(None, min_length=2, max_length=100)
    appointment_date: date
    appointment_time: time

    @field_validator("doctor_name")
    @classmethod 
    def validate_doctor_name(cls, v:str):
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Invalid doctor name")
        return v

    @field_validator("appointment_date")
    @classmethod 
    def validate_date_not_in_past(cls, v:date):
        if v<date.today():
            raise ValueError("Appontments can not be in the past")
        return v
    
    @field_validator("appointment_time" , mode="before")
    @classmethod 
    def validate_time(cls, v):
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            return normalize_hhmm(v)
        raise ValueError("Invalid appoinment time")


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    appointment_id: int = Field(alias="AppointmentID")
    elder_id: int = Field(alias="ElderID")
    doctor_name: str = Field(alias="DoctorName")
    title: str = Field(alias="Title")
    location: Optional[str] = Field(alias="Location")
    notes:Optional[str] = Field(alias="Notes")
    appointment_date: date = Field(alias="AppointmentDate")
    appointment_time: str = Field(alias="AppointmentTime")  

    @field_validator("appointment_time", mode="before")
    @classmethod 
    def validate_time_to_hhmm(cls, v:str):
        if isinstance(v, time):
            return v.strftime("%H:%M")
        if isinstance(v, str):
            v=v.strip()
            if re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$",v):
                return v[:5]
            raise ValueError("Invalid appointment time")
    


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

    @field_validator("appointment_date")
    @classmethod 
    def validate_date_not_in_past(cls, v:Optional[date]):
        if v is None:
            return v
        if v<date.today():
            raise ValueError("Appontments can not be in the past")
        return v
    
    @field_validator("appointment_time", mode="before")
    @classmethod 
    def validate_time(cls, v:Optional[str]):
        if v is None:
            return v
        if isinstance(v, time):
            return v
        if isinstance(v, str):
            return normalize_hhmm(v)
        raise ValueError("Invalid appointment time")

