from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.user import UserResponse, UserWithProfileResponse
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.activity_level import ActivityLevel

router = APIRouter()

@router.get("/me", response_model=UserWithProfileResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение информации о текущем пользователе."""
    result = await db.execute(
        select(UserProfile)
        .options(selectinload(UserProfile.activity_level))
        .filter(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    profile_data = {
        "user_id": profile.user_id if profile else current_user.id,
        "name": profile.name if profile else "",
        "gender": profile.gender if profile else "male",
        "birth_date": profile.birth_date if profile else None,
        "height_cm": profile.height_cm if profile else None,
        "weight_kg": profile.weight_kg if profile else None,
        "activity_level_id": profile.activity_level_id if profile else None,
        # "activity_level_code": "sedentary",
        "activity_level_code": profile.activity_level.code if profile and profile.activity_level else None,
    }
    
    print(profile_data)

    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "profile": profile_data
    }
    
    return user_data

@router.put("/me/profile", response_model=UserWithProfileResponse)
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserProfile)
        .options(selectinload(UserProfile.activity_level))
        .where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Обновление полей
    if 'height_cm' in profile_data:
        profile.height_cm = profile_data['height_cm']

    if 'weight_kg' in profile_data:
        profile.weight_kg = profile_data['weight_kg']

    # Исправьте на activity_level_code
    if 'activity_level_code' in profile_data:
        result = await db.execute(
            select(ActivityLevel).where(
                ActivityLevel.code == profile_data['activity_level_code']
            )
        )
        activity = result.scalar_one_or_none()

        if not activity:
            raise HTTPException(
                status_code=400,
                detail='Invalid activity code'
            )

        profile.activity_level_id = activity.id

    await db.commit()
    await db.refresh(profile)
    
    # Также обновляем связанный объект activity_level
    if profile.activity_level_id:
        await db.refresh(profile, ['activity_level'])

    # Возвращаем обновленные данные пользователя
    profile_data_response = {
        "user_id": profile.user_id,
        "name": profile.name,
        "gender": profile.gender,
        "birth_date": profile.birth_date,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "activity_level_id": profile.activity_level_id,
        "activity_level_code": profile.activity_level.code if profile.activity_level else None,
    }
    
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "profile": profile_data_response
    }
    
    return user_data
