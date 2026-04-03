from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────
    app_name: str = "StudentAttendance"
    app_env: str = "development"  # development | staging | production
    debug: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

    # ── Response compression (local/prod) ───────────────────
    gzip_enabled: bool = True
    gzip_minimum_size: int = 1024
    gzip_compresslevel: int = 5

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
    access_token_expire_minutes: int = 3600

    # ── Forgot password / Mail ──────────────────────────────
    forgot_password_otp_ttl_seconds: int = 300
    mail_provider_type: str = "mailtrap"
    mailtrap_api_key: str = ""
    mailtrap_sender_email: str = ""
    mailtrap_sender_name: str = "StudentAttendance"
    mailtrap_sandbox: bool = True
    mailtrap_inbox_id: int | None = None

    # SMTP provider (dùng khi MAIL_PROVIDER_TYPE=smtp)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_security: str = "tls"  # tls | ssl | none
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender_email: str = ""
    smtp_sender_name: str = "StudentAttendance"
    smtp_timeout_seconds: int = 20

    # ── CORS ────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3001", "http://localhost:5173"]

    # ── AI Demo (hidden page, no class/session dependency) ─
    ai_demo_mode: str = "both"  # webcam | ip_camera | both
    ai_demo_hidden_page_path: str = "/api/v1/attendance/demo/hidden-page"
    ai_demo_image_dir: str = "uploads/student_faces"
    ai_demo_insightface_model: str = "buffalo_l"

    # Matching thresholds
    ai_demo_cosine_threshold: float = 0.45
    ai_demo_match_margin_min: float = 0.03
    ai_demo_student_agg_top_n: int = 3
    ai_demo_face_confidence_min: float = 0.6

    # Quality/adaptive threshold
    ai_demo_quality_face_size_good: int = 100
    ai_demo_quality_face_size_min: int = 60
    ai_demo_quality_threshold_penalty: float = 0.08

    # RTSP tuning
    ai_demo_rtsp_process_interval: float = 0.8
    ai_demo_rtsp_reconnect_delay: float = 3.0
    ai_demo_rtsp_stream_fps: int = 15
    ai_demo_rtsp_frame_width: int = 960
    ai_demo_rtsp_frame_height: int = 540
    ai_demo_rtsp_jpeg_quality: int = 65
    ai_demo_rtsp_read_fail_tolerance: int = 12
    ai_demo_rtsp_capture_preset: str = "stable"  # stable | low_latency
    ai_demo_rtsp_enable_preset_fallback: bool = True
    ai_demo_rtsp_corrupt_frame_tolerance: int = 14
    ai_demo_rtsp_corrupt_min_std: float = 10.0

    # AI demo logging/perf tuning
    ai_demo_debug_log_enabled: bool = True
    ai_demo_debug_log_verbose: bool = False
    ai_demo_debug_log_legacy_mirror: bool = False

    # Confirmation gates
    ai_demo_rtsp_min_det_score: float = 0.70
    ai_demo_rtsp_min_face_size: int = 90
    ai_demo_rtsp_min_face_quality: float = 0.60
    ai_demo_rtsp_min_face_quality_one_shot: float = 0.70
    ai_demo_rtsp_confirm_min_confidence: float = 0.55
    ai_demo_rtsp_one_shot_confidence: float = 0.68
    ai_demo_rtsp_confirm_min_margin: float = 0.04
    ai_demo_rtsp_one_shot_min_margin: float = 0.06
    ai_demo_rtsp_confirm_streak_ttl: float = 2.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
