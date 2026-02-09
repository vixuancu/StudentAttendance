"""
Database engine & session factory với Connection Pool được cấu hình đầy đủ.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

logger = logging.getLogger(__name__)

# ===================== ENGINE + CONNECTION POOL ===================== #
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,                    # Log SQL khi debug
    future=True,
    # ── Connection Pool ──
    pool_size=settings.db_pool_size,        # Số connection thường trực (default 10)
    max_overflow=settings.db_max_overflow,  # Connection tạo thêm khi pool đầy (default 20)
    pool_recycle=settings.db_pool_recycle,  # Tái tạo connection sau N giây (tránh DB timeout)
    pool_pre_ping=settings.db_pool_pre_ping,  # Ping kiểm tra connection còn sống trước khi dùng
    pool_timeout=settings.db_pool_timeout,  # Timeout chờ lấy connection từ pool
)

# ===================== SESSION FACTORY ===================== #
async_session_factory = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,# tránh lỗi "Object is already detached" sau commit
    autocommit=False, # tắt autocommit để kiểm soát transaction thủ công
    autoflush=False, # tắt autoflush để tránh ghi dữ liệu không mong muốn
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency để inject database session – tự động commit/rollback."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()