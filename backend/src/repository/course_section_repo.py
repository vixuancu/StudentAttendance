from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.classroom import Classroom
from src.db.models.course import Course
from src.db.models.course_section import CourseSection
from src.db.models.enrollment import Enrollment
from src.db.models.role import Role
from src.db.models.user import User
from src.repository.base import BaseRepository
from src.repository.interfaces.i_course_section_repo import ICourseSectionRepository


class CourseSectionRepository(BaseRepository, ICourseSectionRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(CourseSection, db)

    async def get_by_id(self, section_id: int):
        result = await self.db.execute(
            select(CourseSection)
            .options(
                selectinload(CourseSection.course),
                selectinload(CourseSection.user),
                selectinload(CourseSection.room),
            )
            .where(CourseSection.id == section_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name_ci(self, name: str):
        normalized = name.strip().lower()
        result = await self.db.execute(
            select(CourseSection).where(func.lower(CourseSection.name) == normalized)
        )
        return result.scalar_one_or_none()

    async def list_sections(
        self,
        skip: int,
        limit: int,
        search: str | None,
        is_cancel: bool | None,
    ):
        enrollment_count = (
            select(func.count(Enrollment.id))
            .where(
                Enrollment.course_section_id == CourseSection.id,
                Enrollment.is_cancel.is_(False),
            )
            .correlate(CourseSection)
            .scalar_subquery()
        )

        query = (
            select(CourseSection, enrollment_count.label("si_so"))
            .options(
                selectinload(CourseSection.course),
                selectinload(CourseSection.user),
                selectinload(CourseSection.room),
            )
            .join(Course, Course.id == CourseSection.course_id)
            .join(User, User.id == CourseSection.user_id)
            .order_by(CourseSection.created_at.desc(), CourseSection.id.desc())
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(
                or_(
                    CourseSection.name.ilike(keyword),
                    Course.course_name.ilike(keyword),
                    User.full_name.ilike(keyword),
                )
            )

        if is_cancel is not None:
            query = query.where(CourseSection.is_cancel.is_(is_cancel))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return [(row[0], int(row[1] or 0)) for row in result.all()]

    async def count_sections(self, search: str | None, is_cancel: bool | None):
        query = (
            select(func.count(CourseSection.id))
            .select_from(CourseSection)
            .join(Course, Course.id == CourseSection.course_id)
            .join(User, User.id == CourseSection.user_id)
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(
                or_(
                    CourseSection.name.ilike(keyword),
                    Course.course_name.ilike(keyword),
                    User.full_name.ilike(keyword),
                )
            )

        if is_cancel is not None:
            query = query.where(CourseSection.is_cancel.is_(is_cancel))

        result = await self.db.execute(query)
        return result.scalar_one() or 0

    async def get_course_by_id(self, course_id: int):
        result = await self.db.execute(
            select(Course).where(Course.id == course_id, Course.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_room_by_id(self, room_id: int):
        result = await self.db.execute(
            select(Classroom).where(
                Classroom.id == room_id,
                Classroom.is_cancel.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_lecturer_by_id(self, user_id: int):
        result = await self.db.execute(
            select(User)
            .join(Role, Role.id == User.role_id)
            .where(
                User.id == user_id,
                User.is_cancel.is_(False),
                Role.is_cancel.is_(False),
                Role.role_name == "giang_vien",
            )
        )
        return result.scalar_one_or_none()

    async def list_course_options(self):
        result = await self.db.execute(
            select(Course)
            .where(Course.is_cancel.is_(False))
            .order_by(Course.course_name.asc())
        )
        return list(result.scalars().all())

    async def list_room_options(self):
        result = await self.db.execute(
            select(Classroom)
            .where(Classroom.is_cancel.is_(False))
            .order_by(Classroom.class_name.asc())
        )
        return list(result.scalars().all())

    async def list_lecturer_options(self):
        result = await self.db.execute(
            select(User)
            .join(Role, Role.id == User.role_id)
            .where(
                User.is_cancel.is_(False),
                Role.is_cancel.is_(False),
                Role.role_name == "giang_vien",
            )
            .order_by(User.full_name.asc(), User.id.asc())
        )
        return list(result.scalars().all())

    async def soft_delete(self, db_obj: CourseSection):
        return await self.update(db_obj, {"is_cancel": True})
