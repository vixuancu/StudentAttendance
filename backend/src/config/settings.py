
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #App
    app_name: str = "StudentAttendance"
    app_env: str = "development"
    debug: bool = True

    #Database
    db_url: str = "postgresql+asyncpg://postgres:123456@localhost:5432/student_attendance"

    #Security
    secret_key: str = "your-secret-key" 
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

    
    