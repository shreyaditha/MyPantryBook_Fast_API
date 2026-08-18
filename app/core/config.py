import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./pantry.db"
    SECRET_KEY: str = "mysecretkey_change_in_production_please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    DEMO_USER_ID: int = 1

    class Config:
        env_file = ".env"


settings = Settings()

# If running on Vercel and DATABASE_URL is still the default relative SQLite path,
# switch to /tmp/pantry.db because the project root on Vercel is read-only.
if os.getenv("VERCEL") and settings.DATABASE_URL == "sqlite+aiosqlite:///./pantry.db":
    settings.DATABASE_URL = "sqlite+aiosqlite:////tmp/pantry.db"

