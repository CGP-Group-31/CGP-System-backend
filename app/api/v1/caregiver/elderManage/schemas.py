from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class ElderDetailsResponse(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    date_of_birth: date
    gender: str
    address: str

class ElderProfileResponse(BaseModel):
    elder_id: int
    blood_type: str
    allergies: str
    chronic_conditions: str
    emergency_notes: str
    past_surgeries: str
    preferred_doctor_id: int

class ElderUpdate(BaseModel):
    full_name: Optional[str]=None
    phone: Optional[str]= Field(None,min_length=10, max_length=10)
    address: Optional[str]=None

class ElderProfileUpdate(BaseModel):
    blood_type: Optional[str]=None
    allergies: Optional[str]=None
    chronic_conditions: Optional[str]=None
    emergency_notes: Optional[str]=None
    past_surgeries: Optional[str]=None
    preferred_doctor_id: Optional[int]=None
