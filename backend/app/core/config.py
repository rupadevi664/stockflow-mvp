from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):

    APP_NAME: str = "StockFlow MVP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "stockflow_db"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = ""

    SECRET_KEY: str = "default_secret_key_for_development_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=(str(BASE_DIR / ".env"), ".env"),
        extra="ignore"
    )


settings = Settings()
