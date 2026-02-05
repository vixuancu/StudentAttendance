from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config.settings import settings

# create async engine
engine = create_async_engine(
    settings.database_url, # Database connection URL
    echo=settings.debug, # Log SQL statements if in debug mode
    future = True
)

# Create async session factory - là chức năng tạo các phiên làm việc với cơ sở dữ liệu
async_session_factory = async_sessionmaker(
    engine, # tạo phiên làm việc với engine đã tạo
    class_=AsyncSession, # sử dụng lớp AsyncSession để làm việc với các phiên không đồng bộ
    expire_on_commit=False, # không làm hết hạn các đối tượng sau khi cam kết
    autocommit=False, # không tự động thay đổi
    autoflush=False # không tự động làm mới các thay đổi
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency để lấy (inject) session database bất đồng bộ"""
    async with async_session_factory() as session:
        try:
            yield session 
            await session.commit() 
        except Exception:
            await session.rollback() 
            raise # ném lại ngoại lệ để xử lý ở nơi khác
        finally:
            await session.close()