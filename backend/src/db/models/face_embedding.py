from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, LargeBinary, BigInteger, ForeignKey, DECIMAL, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, IDMixin

if TYPE_CHECKING:
    from src.db.models.student import Student


class FaceEmbedding(Base, IDMixin):
    __tablename__ = "face_embeddings"

    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    embedding_vector: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    quality_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="face_embeddings")