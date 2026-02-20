
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re

# class ElderCreate(BaseModel):
#     full_name: str = Field(min_length=3, max_length=100)
#     email: EmailStr
#     phone: str = Field(min_length=10, max_length=15)
#     password: str = Field(min_length=6, max_length=72)
#     date_of_birth: date
#     gender: str
#     address: str

# class ElderCreateResponse(BaseModel):
#     user_id: int


# class ElderRelationship(BaseModel):
    
#     elderID : int
#     caregiverTD : int
#     RelationshipType : str
#     IsPrimary : bool

# class ElderRelationshipResponse(BaseModel):
#     relationship_id: int

class ElderRegisterRequest(BaseModel):
    # elder fields
    full_name: str
    email: EmailStr
    phone: str
    password: str
    date_of_birth: date
    gender: str
    address: str

    # relationship fields
    caregiver_id: int
    relationship_type: str
    is_primary: bool

class ElderRegisterResponse(BaseModel):
    user_id: int
    relationship_id: int

class ElderProfile(BaseModel):
    elder_id: int
    blood_etype: str
    allergies: str
    chronic_conditions: str
    emergency_notes: str
    past_surgeries: str
    preferred_doctor_id: int


class ElderProfileResponse(BaseModel):
    profile_id: int

class DoctorResponse(BaseModel):
    doctor_id: int
    full_name: str
    specialization: str
    hospital: str

PHONE_REGEX = re.compile(r"^[0-9+\-\s]{8,12}$")

class EmergencyContactCreate(BaseModel):
    elder_id: int = Field(..., gt=0)
    contact_name: str = Field(..., min_length=2, max_length=50)
    phone: str = Field(..., min_length=8, max_length=12)
    relationship: str = Field(..., min_length=2, max_length=50)
    is_primary: bool = Field(default=False)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):
        v = v.strip()
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone format. Use 8-12 digits")
        return v

    @field_validator("contact_name", "relationship")
    @classmethod
    def no_empty_strings(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty.")
        return v

class EmergencyContactResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contact_id: int
    elder_id: int
    contact_name: str
    phone: str
    relationship: str
    is_primary: bool


class MessageResponse(BaseModel):
    message: str
    class Config:
        populate_by_name = True
        from_attributes = True


class DoctorSearchRequest(BaseModel):
    doctor_name: Optional[str] = None
    hospital: Optional[str] = None