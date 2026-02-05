


from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Enum, ForeignKey, String, BigInteger
from backend.src.db.base import Base, IDMixin, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.db.models.enums import UserRole

class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50),unique=True,nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100),unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255),nullable=False)
    role: Mapped[str] = mapped_column(Enum[UserRole],nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True)

    # Relationships
    lecturer: Mapped[Optional["Lecturer"]] = relationship(back_populates="user")
    
class Lecturer(Base, IDMixin):
    __tablename__ = "lecturers"

    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    lecturer_code: Mapped[str] = mapped_column(String(20),unique=True,nullable=False)
    full_name: Mapped[str] = mapped_column(String(100),nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100),nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20),nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100),nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    # relationships
    user: Mapped[Optional["User"]] = relationship(back_populates="lecturer")
    courses: Mapped[list["Course"]] = relationship(back_populates="lecturer")

# import để tránh lỗi circular import
from backend.src.db.models.course import Course
    
    