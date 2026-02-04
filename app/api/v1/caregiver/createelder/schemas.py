
from pydantic import BaseModel, EmailStr
from datetime import date

from pydantic import BaseModel, Field, EmailStr

class ElderCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15)
    password: str = Field(min_length=6, max_length=72)
    date_of_birth: date
    gender: str
    address: str

class ElderCreateResponse(BaseModel):
    user_id: int


class ElderRelationship(BaseModel):
    
    elderID : int
    caregiverTD : int
    RelationshipType : str
    IsPrimary : bool

class ElderRelationshipResponse(BaseModel):
    relationship_id: int

# class ElderLogin(BaseModel):
#     email: EmailStr
#     password: str

# class ElderLoginResponse(BaseModel):
#     user_id: int
#     role_id: int
#     full_name: str
#     email: EmailStr
#     phone: str
#     address: str
#     date_of_birth: date
#     gender: str
#     createdAt: date