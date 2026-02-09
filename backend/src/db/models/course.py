from datetime import date, datetime, time
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Date, DateTime, Enum, ForeignKey, SmallInteger, String, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, IDMixin
from src.db.models.enums import SessionSlot, SessionStatus

if TYPE_CHECKING:
    from src.db.models.user import Lecturer
    from src.db.models.student import Student
    from src.db.models.attendance import AttendanceRecord, AttendanceEvent


class Course(Base, IDMixin):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("course_code", "semester", name="uq_course_semester"),
    )

    course_code: Mapped[str] = mapped_column(String(20), nullable=False)
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    credits: Mapped[int] = mapped_column(SmallInteger, default=3)
    semester: Mapped[str] = mapped_column(String(20), nullable=False)
    lecturer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("lecturers.id", ondelete="SET NULL"),
        nullable=True
    )
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    lecturer: Mapped[Optional["Lecturer"]] = relationship(back_populates="courses")
    course_students: Mapped[list["CourseStudent"]] = relationship(back_populates="course")
    class_sessions: Mapped[list["ClassSession"]] = relationship(back_populates="course")


class CourseStudent(Base):
    __tablename__ = "course_students"

    course_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="course_students")
    student: Mapped["Student"] = relationship(back_populates="course_students")


class ClassSession(Base, IDMixin):
    __tablename__ = "class_sessions"
    __table_args__ = (
        UniqueConstraint("course_id", "session_date", "session_slot", name="uq_session"),
    )

    course_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    session_slot: Mapped[SessionSlot] = mapped_column(Enum(SessionSlot), nullable=False)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    room: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus),
        default=SessionStatus.PENDING
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="class_sessions")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="session")
    attendance_events: Mapped[list["AttendanceEvent"]] = relationship(back_populates="session")