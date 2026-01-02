from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import List


class Settings(BaseSettings):
    # Database settings
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DIALECT: str
    DB_ASYNC_DRIVER: str
    DB_SYNC_DRIVER: str

    # JWT and Security settings
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
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
        return (
            f"{self.DB_DIALECT}+{self.DB_ASYNC_DRIVER}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    @computed_field
    @property
    def sync_database_url(self) -> str:
        return (
            f"{self.DB_DIALECT}+{self.DB_SYNC_DRIVER}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"
        # Добавляем валидацию для списка CORS origins если это строка в .env
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "BACKEND_CORS_ORIGINS":
                # Если значение приходит как строка, пытаемся преобразовать в список
                if raw_val.startswith("[") and raw_val.endswith("]"):
                    # Убираем квадратные скобки и разбиваем по запятым
                    items = raw_val.strip("[]").split(",")
                    return [item.strip().strip('"').strip("'") for item in items]
            return raw_val


settings = Settings()