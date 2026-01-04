from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password, 
    create_access_token,
    get_password_hash
)
from app.schemas.user import UserRegister, UserResponse, UserWithProfileResponse
from app.schemas.token import Token
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.activity_level import ActivityLevel

router = APIRouter()

@router.post("/register", response_model=UserWithProfileResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя с профилем."""
    # Проверяем, существует ли пользователь

    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создаем пользователя
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    
    db.add(user)
    await db.flush()  # Используем flush вместо commit, чтобы получить ID
    
    # Создаем профиль пользователя
    profile = UserProfile(
        user_id=user.id,
        name=user_data.name,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        height_cm=None,
        weight_kg=None,
        activity_level_id=None
    )
    
    db.add(profile)
    await db.commit()
    await db.refresh(user)
    
    # Получаем профиль для ответа
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "profile": profile
    }

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Аутентификация пользователя."""
    print(form_data.username)
    print(form_data.password)
    
    # Находим пользователя
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout():
    """Выход из системы (на клиенте удаляется токен)."""
    return {"message": "Successfully logged out"}