
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    """Base class cho tất cả models """
    pass

class TimestampMixin:
    """
    Mixin để tái sử dụng các cột created_at và updated_at
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # Sử dụng timezone-aware datetime
        server_default=func.now(),# Thiết lập giá trị mặc định là thời gian hiện tại khi bản ghi được tạo
        nullable=False # Không cho phép giá trị null
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(), # Tự động cập nhật thời gian hiện tại khi bản ghi được cập nhật
        nullable=True
    )

class IDMixin:
    """
    Mixin for auto-increment BigInt ID
    """
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )