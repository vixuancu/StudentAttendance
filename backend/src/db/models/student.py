from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.db.models.enrollment import Enrollment
    from src.db.models.attendance import Attendance
    from src.db.models.student_face import StudentFace


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    birth_of_date: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False))
    gender: Mapped[Optional[bool]] = mapped_column(Boolean)
    administrative_class: Mapped[str] = mapped_column(String(100), nullable=False)
    is_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False), server_default=func.now())
    updated_at: Mapped[Optional[object]] = mapped_column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # Relationships
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")
    attendances: Mapped[list["Attendance"]] = relationship(back_populates="student")
    face_samples: Mapped[list["StudentFace"]] = relationship(back_populates="student")
