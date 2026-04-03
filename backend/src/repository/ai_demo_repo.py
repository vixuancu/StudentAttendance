from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.student import Student
from src.db.models.student_face import StudentFace


class AIDemoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_active_student_faces(self) -> list[dict]:
        result = await self.db.execute(
            select(
                StudentFace.student_id,
                Student.student_code,
                Student.full_name,
                StudentFace.embedding,
            )
            .join(Student, Student.id == StudentFace.student_id)
            .where(Student.is_cancel.is_(False))
            .order_by(Student.id.asc(), StudentFace.id.asc())
        )

        rows = []
        for student_id, student_code, full_name, embedding in result.all():
            rows.append(
                {
                    "student_id": int(student_id),
                    "student_code": student_code,
                    "full_name": full_name,
                    "embedding": embedding,
                }
            )
        return rows

    async def get_active_student_by_id(self, student_id: int) -> Student | None:
        result = await self.db.execute(
            select(Student).where(Student.id == student_id, Student.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def add_student_face(self, student_id: int, image_url: str, embedding: list[float]) -> StudentFace:
        face = StudentFace(
            student_id=student_id,
            image_url=image_url,
            embedding=embedding,
        )
        self.db.add(face)
        await self.db.flush()
        await self.db.refresh(face)
        return face

    async def list_student_faces(self, student_id: int) -> list[StudentFace]:
        result = await self.db.execute(
            select(StudentFace)
            .where(StudentFace.student_id == student_id)
            .order_by(StudentFace.created_at.desc(), StudentFace.id.desc())
        )
        return list(result.scalars().all())
