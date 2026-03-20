from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.user import User


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="role")
