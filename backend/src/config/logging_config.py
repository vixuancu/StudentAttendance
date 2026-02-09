"""
Logging configuration – cấu hình logging cho toàn bộ ứng dụng.
Gọi setup_logging() một lần ở startup (main.py).
"""

import logging
import sys
from pathlib import Path

from src.config.settings import settings


def setup_logging() -> None:
    """
    Cấu hình logging với format rõ ràng.
    - Console: luôn hiện
    - File: ghi vào logs/app.log (nếu thư mục tồn tại)
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Format: [2026-02-09 10:30:45] INFO     src.main | Starting app...
    fmt = "[%(asctime)s] %(levelname)-8s %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))
    handlers.append(console_handler)

    # File handler (nếu thư mục logs/ tồn tại)
    log_dir = Path("logs")
    if log_dir.exists():
        file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True,  # reset existing handlers
    )

    # Giảm noise của thư viện bên thứ ba
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
