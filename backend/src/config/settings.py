from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────
    app_name: str = "StudentAttendance"
    app_env: str = "development"  # development | staging | production
    debug: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

    # ── Database ────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://root:123456@localhost:5432/student_attendance"

    # Connection Pool
    db_pool_size: int = 10            # Số connection thường trực trong pool
    db_max_overflow: int = 20         # Số connection tạo thêm khi pool đầy
    db_pool_recycle: int = 3600       # Tái tạo connection sau N giây (tránh timeout)
    db_pool_pre_ping: bool = True     # Kiểm tra connection còn sống trước khi dùng
    db_pool_timeout: int = 30         # Thời gian chờ lấy connection từ pool (giây)

    # ── Security ────────────────────────────────────────────
    secret_key: str = "your-secret-key"
    access_token_expire_minutes: int = 30

    # ── CORS ────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
