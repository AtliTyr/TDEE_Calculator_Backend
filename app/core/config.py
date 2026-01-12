import os
from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import List, Optional


class Settings(BaseSettings):
    # Railway / prod
    DATABASE_URL: Optional[str] = None

    # Local DB settings
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None

    DB_DIALECT: str = "postgresql"
    DB_ASYNC_DRIVER: str = "asyncpg"
    DB_SYNC_DRIVER: str = "psycopg2"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # Добавляем настройку для refresh token
    ALGORITHM: str = "HS256"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # API settings
    PROJECT_NAME: str = "Metabalance API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    @computed_field
    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace(
                "postgresql://",
                "postgresql+asyncpg://",
            )

        return (
            f"{self.DB_DIALECT}+{self.DB_ASYNC_DRIVER}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    @computed_field
    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace(
                "postgresql://",
                "postgresql+psycopg2://",
            )

        return (
            f"{self.DB_DIALECT}+{self.DB_SYNC_DRIVER}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()