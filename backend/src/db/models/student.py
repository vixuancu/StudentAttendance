from enum import Enum
from typing import Optional
from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.db.base import IDMixin, TimestampMixin, Base
from backend.src.db.models.enums import StudentStatus

class Student(Base, IDMixin, TimestampMixin):
    __tablename__ = "students"

    student_code: Mapped[str] = mapped_column(String(20),unique=True,nullable=False)
    full_name: Mapped[str] = mapped_column(String(100),nullable=False)
    class_code: Mapped[Optional[str]] = mapped_column(String(20),nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100),nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20),nullable=True)
    enrollment_year: Mapped[Optional[int]] = mapped_column(SmallInteger,nullable=True)
    status: Mapped[StudentStatus] = mapped_column(Enum[StudentStatus],default=StudentStatus.ACTIVE)

    # relationships
    face_embeddings: Mapped[list["FaceEmbedding"]] = relationship(back_populates="student")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="student")
    course_students: Mapped[list["CourseStudent"]] = relationship(back_populates="student")

# import để tránh lỗi circular import
from backend.src.db.models.face_embedding import FaceEmbedding
from backend.src.db.models.attendance import AttendanceRecord
from backend.src.db.models.course import CourseStudent