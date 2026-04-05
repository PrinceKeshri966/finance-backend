from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Finance Dashboard API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # SQLite for simplicity; swap DATABASE_URL in .env to use Postgres etc.
    DATABASE_URL: str = "sqlite:///./finance.db"

    # Change this in production — never hardcode secrets in real projects
    SECRET_KEY: str = "please-change-this-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
