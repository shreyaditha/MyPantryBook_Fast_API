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
        extra = "ignore"


settings = Settings()

# On Vercel (or AWS Lambda environment), project root is read-only.
# Redirect default SQLite path to /tmp/pantry.db unless a custom DATABASE_URL is set.
is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("VERCEL_ENV"))
if is_serverless and settings.DATABASE_URL == "sqlite+aiosqlite:///./pantry.db":
    settings.DATABASE_URL = "sqlite+aiosqlite:////tmp/pantry.db"
