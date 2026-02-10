
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

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


class EmergencyContactCreate(BaseModel):
    elder_id: int
    contact_name: str = Field(max_length=100)
    phone: str = Field(min_length=8, max_length=15)
    relationship: Optional[str] = None
    is_primary: bool = False


class EmergencyContactResponse(BaseModel):
    contact_id: int = Field(alias="ContactID")
    elder_id: int = Field(alias="ElderID")
    contact_name: Optional[str] = Field(alias="ContactName")
    phone: str = Field(alias="Phone")
    relationship: Optional[str] = Field(alias="Relationship")
    is_primary: bool = Field(alias="IsPrimary")

    class Config:
        populate_by_name = True
        from_attributes = True