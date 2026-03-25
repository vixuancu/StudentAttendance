from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.student_face import StudentFace
from src.repository.base import BaseRepository
from src.repository.interfaces.i_student_face_repo import IStudentFaceRepository


class StudentFaceRepository(BaseRepository, IStudentFaceRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(StudentFace, db)

    async def get_by_student_id(self, student_id: int) -> list[StudentFace]:
        result = await self.db.execute(
            select(StudentFace)
            .where(StudentFace.student_id == student_id)
            .order_by(StudentFace.created_at.desc(), StudentFace.id.desc())
        )
        return list(result.scalars().all())
