from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, SmallInteger, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.student import Student
    from src.db.models.class_session import ClassSession


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=False)
    class_session_id: Mapped[int] = mapped_column(Integer, ForeignKey("class_session.id"), nullable=False)
    status: Mapped[Optional[int]] = mapped_column(SmallInteger)
    note: Mapped[Optional[str]] = mapped_column(String(255))
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="attendances")
    class_session: Mapped["ClassSession"] = relationship(back_populates="attendances")
