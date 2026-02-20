from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class CaregiverProfileResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    gender: str
    created_at: date

class CaregiverProfileUpdate(BaseModel):
    full_name:Optional[str]=None
    phone: Optional[str]=Field(None, min_length=10, max_length=10)
    address: Optional[str]


#class CaregiverPasswordRequest(BaseModel):
 #   old_pwd: str
  #  new_pwd: str
