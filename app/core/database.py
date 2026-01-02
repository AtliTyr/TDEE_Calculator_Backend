from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Асинхронный движок
async_engine = create_async_engine(settings.async_database_url)

# Синхронный движок
sync_engine = create_engine(settings.sync_database_url)

# Асинхронная фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Синхронная фабрика сессий
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
    autoflush=False
)

# Асинхронная зависимость для FastAPI
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Синхронная зависимость для синхронных операций
def get_sync_db() -> Session:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Для совместимости оставим get_db как get_async_db
get_db = get_async_db