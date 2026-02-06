
from pydantic import BaseModel, EmailStr
from datetime import date

from pydantic import BaseModel, Field, EmailStr

class ElderLogin(BaseModel):
    email: EmailStr
    password: str

class ElderLoginResponse(BaseModel):
    user_id: int
    role_id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str
    date_of_birth: date
    gender: str
    createdAt: date