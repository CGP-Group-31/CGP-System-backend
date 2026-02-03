
from pydantic import BaseModel, EmailStr
from datetime import date

from pydantic import BaseModel, Field, EmailStr

class CaregiverCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=6, max_length=72)
    date_of_birth: date
    gender: str

class CaregiverCreateResponse(BaseModel):
    user_id: int
