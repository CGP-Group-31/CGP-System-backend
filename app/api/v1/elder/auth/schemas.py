
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

class ElderLogin(BaseModel):
    email: EmailStr
    password: str
    fcm_token: Optional[str] = None
    app_type: str
    device_model: Optional[str] = None

class ElderLoginResponse(BaseModel):
    user_id: int
    role_id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str
    date_of_birth: date
    gender: str
    created_at: datetime