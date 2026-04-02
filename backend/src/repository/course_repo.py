from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.course import Course
from src.repository.base import BaseRepository
from src.repository.interfaces.i_course_repo import ICourseRepository


class CourseRepository(BaseRepository, ICourseRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(Course, db)

    async def get_by_id(self, course_id: int):
        result = await self.db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    async def get_by_name_ci(self, course_name: str):
        normalized = course_name.strip().lower()
        result = await self.db.execute(
            select(Course).where(func.lower(Course.course_name) == normalized)
        )
        return result.scalar_one_or_none()

    async def list_courses(self, skip: int, limit: int, search: str | None, is_cancel: bool | None):
        query = select(Course).order_by(Course.created_at.desc(), Course.id.desc())
        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(Course.course_name.ilike(keyword))
        if is_cancel is not None:
            query = query.where(Course.is_cancel.is_(is_cancel))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_courses(self, search: str | None, is_cancel: bool | None):
        query = select(func.count(Course.id))
        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(Course.course_name.ilike(keyword))
        if is_cancel is not None:
            query = query.where(Course.is_cancel.is_(is_cancel))
        result = await self.db.execute(query)
        return result.scalar_one() or 0