from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, SmallInteger, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.classroom import Classroom


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    camera_status: Mapped[Optional[int]] = mapped_column(SmallInteger)
    is_cancel: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    classrooms: Mapped[list["Classroom"]] = relationship(back_populates="camera")
