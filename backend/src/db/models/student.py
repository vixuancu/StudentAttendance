from typing import Optional, TYPE_CHECKING
from sqlalchemy import SmallInteger, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, IDMixin, TimestampMixin
from src.db.models.enums import StudentStatus

if TYPE_CHECKING:
    from src.db.models.face_embedding import FaceEmbedding
    from src.db.models.attendance import AttendanceRecord
    from src.db.models.course import CourseStudent


class Student(Base, IDMixin, TimestampMixin):
    __tablename__ = "students"

    student_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    class_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    enrollment_year: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[StudentStatus] = mapped_column(
        Enum(StudentStatus),
        default=StudentStatus.ACTIVE
    )

    # Relationships
    face_embeddings: Mapped[list["FaceEmbedding"]] = relationship(back_populates="student")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(back_populates="student")
    course_students: Mapped[list["CourseStudent"]] = relationship(back_populates="student")