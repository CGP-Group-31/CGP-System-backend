from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date
import re

PHONE_REGEX = re.compile(r"^[0-9+\-\s]{8,12}$")
NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z\s\.\-']{1,99}")

class ElderDetailsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    full_name: str = Field(alias="FullName")
    email: EmailStr = Field(alias="Email")
    phone: str = Field(alias="Phone")
    date_of_birth: date = Field(alias="DateOfBirth")
    gender: str = Field(alias="Gender")
    address: str = Field(alias="Address")

class ElderProfileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    elder_id: int = Field(alias="ElderID")
    blood_type: str = Field(alias="BloodTyoe")
    allergies: str = Field(alias="Allergies")
    chronic_conditions: str = Field(alias="ChronicConditions")
    emergency_notes: str = Field(alias="EmergencyNotes")
    past_surgeries: str = Field(alias="Pastsurgeries")
    preferred_doctor_id: int = Field(alias="PreferredDoctorID")

class ElderUpdate(BaseModel):
    full_name: Optional[str]= Field(None, min_length=3, max_length=100)
    phone: Optional[str]= Field(None,min_length=8, max_length=12)
    address: Optional[str]=Field(None, min_length=3, max_length=200)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        v=v.strip()
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone format")
        return v
        

    @field_validator("full_name")
    @classmethod 
    def validate_name(cls, v:str):
        if v is None:
            return v
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Invalid name")
        return v

class ElderProfileUpdate(BaseModel):
    blood_type: Optional[str]=Field(None, min_length=1, max_length=3)
    allergies: Optional[str]=Field(None, max_length=500)
    chronic_conditions: Optional[str]=Field(None, max_length=500)
    emergency_notes: Optional[str]=Field(None, max_length=500)
    past_surgeries: Optional[str]=Field(None, max_length=500)
    preferred_doctor_id: Optional[int]=Field(None, gt=0)

    @field_validator("blood_type")
    @classmethod
    def check_letters_only(cls, v):
        if v is None:
            return v
        if not re.match('^[a-zA-Z]+$',v):
            raise ValueError('Only letter allowed')
        return v
