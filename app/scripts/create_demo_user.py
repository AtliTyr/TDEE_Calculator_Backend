from datetime import date, datetime, timedelta, UTC
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import uuid  # Добавляем импорт uuid
import bcrypt

from app.core.config import settings
# Импортируем модели по отдельности, чтобы избежать циклических импортов
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.calculation import Calculation

def hash_password(password: str) -> str:
    s = bcrypt.gensalt()
    h = bcrypt.hashpw(password.encode('utf-8'), s)
    return h.decode('utf-8')

def create_demo_user():
    engine = create_engine(settings.sync_database_url.replace("+asyncpg", ""))
    session = Session(engine)

    try:
        email = "demo@test.com"

        # Проверяем существование пользователя
        existing = session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing:
            print("Демо пользователь уже существует. Удаляем пользователя.")
            session.execute(delete(User).where(User.email == email))
            
        password = "demo123"
        user = User(
            email=email,
            password_hash=hash_password(password),
        )
        session.add(user)
        session.flush()  # Генерируем ID в БД
        
        print(f"user.id: {user.id}")
        
        # Создаем профиль пользователя
        profile = UserProfile(
            user_id=user.id,
            name="Демо Пользователь",
            gender="male",
            birth_date=date(1994, 6, 15),
            height_cm=178,
            activity_level_id=3,
        )
        session.add(profile)

        now = datetime.now(UTC)

        # Создаем несколько расчетов
        for i in range(5):
            weight = 82 - i * 0.5
            age = (datetime.now(UTC).date() - date(1994, 6, 15)).days // 365  # Рассчитываем возраст

            calc = Calculation(
                id=uuid.uuid4(),
                user_id=user.id,
                goal_id=1,
                formula_used="mifflin_st_jeor",
                input_data={
                    "weight": weight,
                    "height": 178,
                    "age": age,
                    "gender": "male",
                    "activity_level": "moderate",
                    "goal": "cut",
                },
                results={
                    "bmr": round(10 * weight + 6.25 * 178 - 5 * age + 5, 1),
                    "tdee": round(
                        (10 * weight + 6.25 * 178 - 5 * age + 5) * 1.55, 1
                    ),
                    "target_calories": 2100 - i * 50,
                },
                created_at=now - timedelta(days=7 * i),
            )
            session.add(calc)

        session.commit()
        print("Демо пользователь успешно создал.")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при создании тестового пользователя: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    create_demo_user()