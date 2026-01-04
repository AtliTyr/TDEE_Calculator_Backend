# app/schemas/__init__.py
from app.schemas.user import (
    UserBase, UserRegister, UserLogin, 
    UserResponse, UserProfileBase, 
    UserProfileCreate, UserProfileResponse,
    UserWithProfileResponse
)
from app.schemas.token import Token, TokenData
from app.schemas.activity_level import (
    ActivityLevelBase, ActivityLevelCreate,
    ActivityLevelResponse, ActivityLevelUpdate
)
from app.schemas.calculation import (
    CalculationBase, CalculationCreate, 
    CalculationResponse, CalculationHistoryResponse, CalculationStatsResponse
)
__all__ = [
    # User schemas
    "UserBase", "UserRegister", "UserLogin", 
    "UserResponse", "UserProfileBase", 
    "UserProfileCreate", "UserProfileResponse",
    "UserWithProfileResponse",
    
    # Token schemas
    "Token", "TokenData",
    
    # Activity level schemas
    "ActivityLevelBase", "ActivityLevelCreate",
    "ActivityLevelResponse", "ActivityLevelUpdate",

    # Calculation schemas
    "CalculationBase", "CalculationCreate", 
    "CalculationResponse", "CalculationHistoryResponse", 
    "CalculationStatsResponse"
]