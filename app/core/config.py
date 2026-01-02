from pydantic_settings import BaseSettings
from pydantic import computed_field


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DIALECT: str
    DB_ASYNC_DRIVER: str
    DB_SYNC_DRIVER: str

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


settings = Settings()