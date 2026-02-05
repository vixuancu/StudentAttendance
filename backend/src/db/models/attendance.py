from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DECIMAL, BigInteger, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.db.base import Base, IDMixin, TimestampMixin
from src.db.models.enums import AttendanceStatus, DetectedByType

if TYPE_CHECKING:
    from src.db.models.course import ClassSession
    from src.db.models.student import Student
    from src.db.models.user import User


class AttendanceRecord(Base, IDMixin, TimestampMixin):
    __tablename__ = "attendance_records"

    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus),
        default=AttendanceStatus.ABSENT,
        nullable=False
    )
    detected_by: Mapped[Optional[DetectedByType]] = mapped_column(
        Enum(DetectedByType),
        nullable=True
    )
    detected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    confirmed_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    session: Mapped["ClassSession"] = relationship(back_populates="attendance_records")
    student: Mapped["Student"] = relationship(back_populates="attendance_records")
    confirmed_by_user: Mapped[Optional["User"]] = relationship()


class AttendanceEvent(Base, IDMixin):
    __tablename__ = "attendance_events"

    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("class_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    student_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="SET NULL"),
        nullable=True
    )
    confidence: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 4), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bounding_box: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    session: Mapped["ClassSession"] = relationship(back_populates="attendance_events")
    student: Mapped[Optional["Student"]] = relationship()