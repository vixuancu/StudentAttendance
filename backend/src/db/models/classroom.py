from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.camera import Camera
    from src.db.models.course_section import CourseSection
    from src.db.models.class_session import ClassSession


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    camera_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cameras.id"))
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    camera: Mapped[Optional["Camera"]] = relationship(back_populates="classrooms")
    course_sections: Mapped[list["CourseSection"]] = relationship(back_populates="room")
    class_sessions: Mapped[list["ClassSession"]] = relationship(back_populates="room")
