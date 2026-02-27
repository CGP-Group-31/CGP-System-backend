from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ElderLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=30)
    fcm_token: Optional[str] = None
    app_type: str
    device_model: Optional[str] = None
    timezone_name: str
    timezone_offset: str
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
    relationshipid: Optional[int] = None
    caregiverid: Optional[int] = None