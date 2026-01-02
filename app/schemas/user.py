from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

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
    birth_date: str
    height_cm: int
    activity_level_id: int

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    user_id: UUID
    
    class Config:
        from_attributes = True

class UserWithProfileResponse(UserResponse):
    profile: Optional[UserProfileResponse] = None