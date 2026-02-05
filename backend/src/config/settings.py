
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #App
    app_name: str = "StudentAttendance"
    app_env: str = "development"
    debug: bool = True

    #Database
    database_url: str = "postgresql+asyncpg://root:123456@localhost:5432/student_attendance"

    #Security
    secret_key: str = "your-secret-key" 
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra="ignore"  # Bỏ qua các biến thừa trong .env

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

    
    