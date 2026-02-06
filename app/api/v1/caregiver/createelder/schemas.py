
from pydantic import BaseModel, EmailStr
from datetime import date

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

