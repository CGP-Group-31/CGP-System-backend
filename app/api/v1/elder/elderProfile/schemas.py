from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date

class CaregiverRelatedResponse(BaseModel):
    model_config= ConfigDict(populate_by_name=True)
    caregiver_id: int = Field(alias="CaregiverID")
    full_name: str = Field(alias="CaregiverFullName")
    relationship_type: str = Field(alias="RelationshipType")
    is_primary: bool = Field(alias="IsPrimary")

class ElderProfileResponse(BaseModel):
    model_config= ConfigDict(populate_by_name=True)
    user_id: int = Field(alias="UserID")
    full_name: str = Field(alias="ElderFullName")
    email: EmailStr = Field(alias="Email")
    phone: str = Field(alias="Phone")
    date_of_birth: date = Field(alias="DateOfBirth")
    address: str = Field(alias="Address")
    gender: str = Field(alias="Gender")
    caregiver: Optional[CaregiverRelatedResponse] =None


