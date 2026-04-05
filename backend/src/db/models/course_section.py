from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.course import Course
    from src.db.models.classroom import Classroom
    from src.db.models.user import User
    from src.db.models.enrollment import Enrollment
    from src.db.models.class_session import ClassSession
    from src.db.models.course_section_schedule import CourseSectionSchedule


class CourseSection(Base):
    __tablename__ = "course_section"
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="chk_time"),
        CheckConstraint("start_date < end_date", name="chk_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classrooms.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[object] = mapped_column(DateTime(timezone=False), nullable=False)
    end_date: Mapped[object] = mapped_column(DateTime(timezone=False), nullable=False)
    start_period: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_periods: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    end_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )
    updated_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="course_sections")
    room: Mapped["Classroom"] = relationship(back_populates="course_sections")
    user: Mapped["User"] = relationship(back_populates="course_sections")
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course_section"
    )
    class_sessions: Mapped[list["ClassSession"]] = relationship(
        back_populates="course_section"
    )
    schedules: Mapped[list["CourseSectionSchedule"]] = relationship(
        back_populates="course_section"
    )
