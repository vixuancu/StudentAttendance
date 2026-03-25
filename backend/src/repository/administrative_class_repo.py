from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.administrative_class import AdministrativeClass
from src.db.models.student import Student
from src.repository.base import BaseRepository
from src.repository.interfaces.i_administrative_class_repo import IAdministrativeClassRepository


class AdministrativeClassRepository(BaseRepository, IAdministrativeClassRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(AdministrativeClass, db)

    async def get_by_id(self, class_id: int):
        result = await self.db.execute(
            select(AdministrativeClass).where(AdministrativeClass.id == class_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name_ci(self, name: str):
        normalized = name.strip().lower()
        result = await self.db.execute(
            select(AdministrativeClass).where(func.lower(AdministrativeClass.name) == normalized)
        )
        return result.scalar_one_or_none()

    async def list_classes(self, skip: int, limit: int, search: str | None, is_cancel: bool | None):
        query = select(AdministrativeClass).order_by(AdministrativeClass.created_at.desc(), AdministrativeClass.id.desc())
        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(AdministrativeClass.name.ilike(keyword))
        if is_cancel is not None:
            query = query.where(AdministrativeClass.is_cancel.is_(is_cancel))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_classes(self, search: str | None, is_cancel: bool | None):
        query = select(func.count(AdministrativeClass.id))
        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(AdministrativeClass.name.ilike(keyword))
        if is_cancel is not None:
            query = query.where(AdministrativeClass.is_cancel.is_(is_cancel))
        result = await self.db.execute(query)
        return result.scalar_one() or 0

    async def count_students_by_class_ids(self, class_ids: list[int]) -> dict[int, int]:
        if not class_ids:
            return {}
        result = await self.db.execute(
            select(Student.administrative_class_id, func.count(Student.id))
            .where(Student.administrative_class_id.in_(class_ids))
            .group_by(Student.administrative_class_id)
        )
        rows = result.all()
        return {int(class_id): int(total) for class_id, total in rows if class_id is not None}

    async def count_students_by_class_id(self, class_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Student.id)).where(Student.administrative_class_id == class_id)
        )
        return result.scalar_one() or 0
