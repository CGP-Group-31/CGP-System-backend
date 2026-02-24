from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

from typing import Optional, List


class CaregiverCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=6, max_length=72)
    date_of_birth: date
    gender: str = Field(min_length=1)
    address: str = Field(min_length=3)
    fcm_token: Optional[str] = None
    app_type: str = Field(min_length=3)
    device_model: Optional[str] = None


class CaregiverCreateResponse(BaseModel):
    user_id: int


class CaregiverLogin(BaseModel):
    email: EmailStr
    password: str
    fcm_token: Optional[str] = None
    app_type: str
    device_model: Optional[str] = None


class RelationshipResponse(BaseModel):
    relationship_id: int
    elder_id: int
    caregiver_id: int


class CaregiverLoginResponse(BaseModel):
    user_id: int
    role_id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str
    date_of_birth: date
    gender: str
    created_at: datetime  
    relationships: List[RelationshipResponse]
