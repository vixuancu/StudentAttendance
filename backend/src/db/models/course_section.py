from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.course import Course
    from src.db.models.classroom import Classroom
    from src.db.models.user import User
    from src.db.models.enrollment import Enrollment
    from src.db.models.class_session import ClassSession


class CourseSection(Base):
    __tablename__ = "course_section"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("classrooms.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer)
    start_date: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    start_period: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_periods: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True))
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="course_sections")
    room: Mapped["Classroom"] = relationship(back_populates="course_sections")
    user: Mapped["User"] = relationship(back_populates="course_sections")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course_section")
    class_sessions: Mapped[list["ClassSession"]] = relationship(back_populates="course_section")
