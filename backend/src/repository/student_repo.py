from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.db.models.administrative_class import AdministrativeClass
from src.db.models.student import Student
from src.db.models.student_face import StudentFace
from src.repository.base import BaseRepository
from src.repository.interfaces.i_student_repo import IStudentRepository


class StudentRepository(BaseRepository, IStudentRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)

    async def get_by_id(self, id: int):
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.administrative_class))
            .where(Student.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip=0, limit=100, filters=None):
        query = select(Student).options(selectinload(Student.administrative_class))
        if filters:
            for f in filters:
                query = query.where(f)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_administrative_class_by_id(self, class_id: int):
        result = await self.db.execute(
            select(AdministrativeClass).where(
                AdministrativeClass.id == class_id,
                AdministrativeClass.is_cancel.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_administrative_classes(self):
        result = await self.db.execute(
            select(AdministrativeClass)
            .where(AdministrativeClass.is_cancel.is_(False))
            .order_by(AdministrativeClass.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_student_code(self, student_code: str):
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.administrative_class))
            .where(Student.student_code == student_code)
        )
        return result.scalar_one_or_none()

    async def count_faces_by_student_ids(self, student_ids: list[int]) -> dict[int, int]:
        if not student_ids:
            return {}

        result = await self.db.execute(
            select(StudentFace.student_id, func.count(StudentFace.id))
            .where(StudentFace.student_id.in_(student_ids))
            .group_by(StudentFace.student_id)
        )
        rows = result.all()
        return {int(student_id): int(total) for student_id, total in rows}

    async def get_existing_student_codes_ci(self, codes: list[str]) -> set[str]:
        normalized = [code.strip().lower() for code in codes if code and code.strip()]
        if not normalized:
            return set()

        result = await self.db.execute(
            select(Student.student_code).where(func.lower(Student.student_code).in_(normalized))
        )
        return {str(code).strip().lower() for code in result.scalars().all()}
