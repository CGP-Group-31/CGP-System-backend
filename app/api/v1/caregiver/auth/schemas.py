
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
# add fcm token with login and the signup
class CaregiverCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=6, max_length=72)
    date_of_birth: date
    gender: str
    address: str
    fcm_token: Optional[str] = None
    app_type: str # 'elder_app', 'caregiver_app'
    device_model: Optional[str] = None

class CaregiverCreateResponse(BaseModel):
    user_id: int



class CaregiverLogin(BaseModel):
    email: EmailStr
    password: str
    fcm_token: Optional[str] = None
    app_type: str
    device_model: Optional[str] = None

class CaregiverLoginResponse(BaseModel):
    user_id: int
    role_id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str
    date_of_birth: date
    gender: str
    createdAt: date
    

   