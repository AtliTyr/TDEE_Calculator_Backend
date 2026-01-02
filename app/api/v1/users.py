from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.user import UserResponse, UserWithProfileResponse
from app.models.user import User
from app.models.user_profile import UserProfile

router = APIRouter()

@router.get("/me", response_model=UserWithProfileResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о текущем пользователе."""
    # Получаем профиль пользователя
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "profile": profile
    }
    
    return user_data

@router.put("/me/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление профиля пользователя."""
    # Находим или создаем профиль
    result = await db.execute(
        select(UserProfile).filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        # Обновляем существующий профиль
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
    else:
        # Создаем новый профиль
        profile = UserProfile(
            user_id=current_user.id,
            **profile_data
        )
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    
    return {"message": "Profile updated successfully", "profile": profile}