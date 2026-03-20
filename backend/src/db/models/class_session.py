from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, SmallInteger, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.course_section import CourseSection
    from src.db.models.classroom import Classroom
    from src.db.models.attendance import Attendance


class ClassSession(Base):
    __tablename__ = "class_session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_section_id: Mapped[int] = mapped_column(Integer, ForeignKey("course_section.id"), nullable=False)
    room_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("classrooms.id"))
    session_date: Mapped[object] = mapped_column(DateTime(timezone=False), nullable=False)
    start_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    end_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    late_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    status: Mapped[Optional[int]] = mapped_column(SmallInteger)
    note: Mapped[Optional[str]] = mapped_column(Text)
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relationships
    course_section: Mapped["CourseSection"] = relationship(back_populates="class_sessions")
    room: Mapped[Optional["Classroom"]] = relationship(back_populates="class_sessions")
    attendances: Mapped[list["Attendance"]] = relationship(back_populates="class_session")
