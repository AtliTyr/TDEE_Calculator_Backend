from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from datetime import datetime, date
from typing import Optional
import datetime as dt

class UserBase(BaseModel):
    email: EmailStr

class UserRegister(UserBase):
    password: str
    name: str
    gender: str
    birth_date: date

    @field_validator('gender')
    def validate_gender(cls, v):
        if v not in ['male', 'female']:
            raise ValueError('Gender must be either "male" or "female"')
        return v

    @field_validator('birth_date')
    def validate_birth_date(cls, v):
        if v > dt.date.today():
            raise ValueError('Birth date cannot be in the future')
        if v < dt.date(1900, 1, 1):
            raise ValueError('Birth date cannot be before 1900')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileBase(BaseModel):
    name: str
    gender: str
    birth_date: date
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    activity_level_id: Optional[int] = None
    activity_level_code: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    user_id: UUID
    
    class Config:
        from_attributes = True

class UserWithProfileResponse(UserResponse):
    profile: Optional[UserProfileResponse] = None