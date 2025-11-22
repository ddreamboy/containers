import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ELogLevel(str):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Класс для хранения и валидации настроек приложения
    Загружает переменные из .env файла
    """
    
    HABR_ADAPTER_PORT: int = 7000

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    PROXY_URL: str | None = None
    DEV_MODE: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def CONSOLE_LOG_LEVEL(self):
        return ELogLevel.DEBUG if self.DEV_MODE else ELogLevel.WARNING

    @property
    def BASE_DIR(self):
        return os.path.dirname(os.path.abspath(__file__))

    @property
    def LOGS_DIR(self):
        return os.path.join(self.BASE_DIR, "logs")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
