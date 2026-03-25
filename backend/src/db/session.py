import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config.settings import settings

logger = logging.getLogger(__name__)

# ===================== ENGINE + CONNECTION POOL ===================== #
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=settings.db_pool_pre_ping,
    pool_timeout=settings.db_pool_timeout,
    connect_args={
        "server_settings": {
            "timezone": "Asia/Ho_Chi_Minh",
        },
        # Nếu dùng cổng 6543 (Transaction), hãy bỏ comment dòng dưới:
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    },
)

# ===================== SESSION FACTORY ===================== #
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency inject database session – tự động commit/rollback."""
    async with async_session_factory() as session:
        try:
            yield session
            if session.is_active:
                await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
