from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date
import re

PHONE_REGEX = re.compile(r"^[0-9+\-\s]{10,12}$")
NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z\s\.\-']{1,99}")

class CaregiverProfileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: int = Field(alias="UserID")
    full_name: str = Field(alias="FullName")
    email: EmailStr = Field(alias="Email")
    address: str = Field(alias="Address")
    phone: str = Field(alias="Phone")
    date_of_birth: date = Field(alias="DateOfBirth")
    gender: str = Field(alias="Gender")

class CaregiverProfileUpdate(BaseModel):
    full_name:Optional[str]=Field(None, min_length=3, max_length=100)
    phone: Optional[str]=Field(None, min_length=10, max_length=12)
    address: Optional[str] = Field(None, min_length=0, max_length=200)
    email: Optional[EmailStr] = Field(None, min_length=3, max_length=200)
    password: Optional[str] = Field(None, min_length=3, max_length=200)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if v is None:
            return v
        v=v.strip().replace(" ","").replace("-","")
        if not PHONE_REGEX.fullmatch(v):
            raise ValueError("Invalid phone format")
        return v

    @field_validator("full_name")
    @classmethod 
    def validate_name(cls, v:Optional[str]):
        if v is None:
            return v
        v = v.strip()
        if not NAME_REGEX.match(v):
            raise ValueError("Invalid  name")
        return v
    

    @field_validator("email")
    @classmethod 
    def normalize_email(cls, v:Optional[EmailStr]):
        if v is None:
            return v
        return v.lower().strip()
    
    
    @field_validator("password")
    @classmethod 
    def password_check(cls, v:Optional[str]):
        if v is None:
            return v
        v=v.strip()
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d",v):
            raise ValueError("Password must contain atleast 1 letter and 1 number")
        return v
       

