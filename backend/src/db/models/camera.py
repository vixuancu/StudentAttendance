from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    Integer,
    SmallInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.classroom import Classroom


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(255), nullable=False)
    camera_stream_url: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("''")
    )
    camera_status: Mapped[Optional[int]] = mapped_column(SmallInteger)
    classroom_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classrooms.id"), unique=True, nullable=False
    )
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )
    updated_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    classrooms: Mapped[list["Classroom"]] = relationship(back_populates="camera")
