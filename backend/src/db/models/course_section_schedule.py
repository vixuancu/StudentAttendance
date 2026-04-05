from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.classroom import Classroom
    from src.db.models.course_section import CourseSection
    from src.db.models.user import User


class CourseSectionSchedule(Base):
    __tablename__ = "course_section_schedule"
    __table_args__ = (
        CheckConstraint(
            "day_of_week >= 2 AND day_of_week <= 8", name="chk_css_day_of_week"
        ),
        CheckConstraint("start_period >= 1", name="chk_css_start_period"),
        CheckConstraint("number_of_periods >= 1", name="chk_css_number_of_periods"),
        CheckConstraint(
            "start_time IS NULL OR end_time IS NULL OR start_time < end_time",
            name="chk_css_time",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_section_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_section.id"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_period: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_periods: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    end_time: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    room_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("classrooms.id"))
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    course_section: Mapped["CourseSection"] = relationship(back_populates="schedules")
    room: Mapped[Optional["Classroom"]] = relationship(
        back_populates="course_section_schedules"
    )
    user: Mapped["User"] = relationship()
