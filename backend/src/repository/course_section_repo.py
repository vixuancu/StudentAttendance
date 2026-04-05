from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.classroom import Classroom
from src.db.models.course import Course
from src.db.models.course_section import CourseSection
from src.db.models.course_section_schedule import CourseSectionSchedule
from src.db.models.enrollment import Enrollment
from src.db.models.role import Role
from src.db.models.student import Student
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
                selectinload(CourseSection.schedules).selectinload(
                    CourseSectionSchedule.user
                ),
                selectinload(CourseSection.schedules).selectinload(
                    CourseSectionSchedule.room
                ),
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
                selectinload(CourseSection.schedules).selectinload(
                    CourseSectionSchedule.user
                ),
                selectinload(CourseSection.schedules).selectinload(
                    CourseSectionSchedule.room
                ),
            )
            .join(Course, Course.id == CourseSection.course_id)
            .join(User, User.id == CourseSection.user_id)
            .order_by(CourseSection.created_at.desc(), CourseSection.id.desc())
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(CourseSection.name.ilike(keyword))

        if is_cancel is not None:
            query = query.where(CourseSection.is_cancel.is_(is_cancel))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return [(row[0], int(row[1] or 0)) for row in result.all()]

    async def count_sections(
        self,
        search: str | None,
        is_cancel: bool | None,
    ):
        query = (
            select(func.count(CourseSection.id))
            .select_from(CourseSection)
            .join(Course, Course.id == CourseSection.course_id)
            .join(User, User.id == CourseSection.user_id)
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(CourseSection.name.ilike(keyword))

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

    @staticmethod
    def _build_schedule_overlap_filters(
        *,
        day_of_week: int,
        start_date: datetime,
        end_date: datetime,
        start_period: int,
        number_of_periods: int,
    ):
        new_end_period = start_period + number_of_periods
        existing_end_period = (
            CourseSectionSchedule.start_period + CourseSectionSchedule.number_of_periods
        )
        return (
            CourseSection.is_cancel.is_(False),
            CourseSectionSchedule.is_cancel.is_(False),
            CourseSectionSchedule.day_of_week == day_of_week,
            CourseSection.start_date <= end_date,
            CourseSection.end_date >= start_date,
            CourseSectionSchedule.start_period < new_end_period,
            existing_end_period > start_period,
        )

    async def get_lecturer_schedule_conflict(
        self,
        *,
        user_id: int,
        day_of_week: int,
        start_date: datetime,
        end_date: datetime,
        start_period: int,
        number_of_periods: int,
        exclude_section_id: int | None = None,
    ):
        query = (
            select(CourseSection)
            .join(
                CourseSectionSchedule,
                CourseSectionSchedule.course_section_id == CourseSection.id,
            )
            .where(
                CourseSectionSchedule.user_id == user_id,
                *self._build_schedule_overlap_filters(
                    day_of_week=day_of_week,
                    start_date=start_date,
                    end_date=end_date,
                    start_period=start_period,
                    number_of_periods=number_of_periods,
                ),
            )
            .order_by(CourseSection.created_at.desc(), CourseSection.id.desc())
        )

        if exclude_section_id is not None:
            query = query.where(CourseSection.id != exclude_section_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_room_schedule_conflict(
        self,
        *,
        room_id: int,
        day_of_week: int,
        start_date: datetime,
        end_date: datetime,
        start_period: int,
        number_of_periods: int,
        exclude_section_id: int | None = None,
    ):
        query = (
            select(CourseSection)
            .join(
                CourseSectionSchedule,
                CourseSectionSchedule.course_section_id == CourseSection.id,
            )
            .where(
                CourseSectionSchedule.room_id == room_id,
                *self._build_schedule_overlap_filters(
                    day_of_week=day_of_week,
                    start_date=start_date,
                    end_date=end_date,
                    start_period=start_period,
                    number_of_periods=number_of_periods,
                ),
            )
            .order_by(CourseSection.created_at.desc(), CourseSection.id.desc())
        )

        if exclude_section_id is not None:
            query = query.where(CourseSection.id != exclude_section_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def replace_schedules(
        self,
        section_id: int,
        schedules: list[dict],
    ) -> None:
        await self.db.execute(
            delete(CourseSectionSchedule).where(
                CourseSectionSchedule.course_section_id == section_id
            )
        )

        if not schedules:
            await self.db.flush()
            return

        objects = []
        for item in schedules:
            payload = {
                "course_section_id": section_id,
                "user_id": item.get("user_id"),
                "day_of_week": item["day_of_week"],
                "start_period": item["start_period"],
                "number_of_periods": item["number_of_periods"],
                "start_time": item.get("start_time"),
                "end_time": item.get("end_time"),
                "room_id": item.get("room_id"),
                "is_cancel": bool(item.get("is_cancel", False)),
            }
            objects.append(CourseSectionSchedule(**payload))

        self.db.add_all(objects)
        await self.db.flush()

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

    async def list_enrolled_students(
        self,
        section_id: int,
        skip: int,
        limit: int,
        search: str | None,
    ) -> list[Student]:
        query = (
            select(Student)
            .join(
                Enrollment,
                Enrollment.student_id == Student.id,
            )
            .options(selectinload(Student.administrative_class))
            .where(
                Enrollment.course_section_id == section_id,
                Enrollment.is_cancel.is_(False),
                Student.is_cancel.is_(False),
            )
            .order_by(Student.full_name.asc(), Student.id.asc())
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Student.student_code.ilike(keyword),
                    Student.full_name.ilike(keyword),
                )
            )

        result = await self.db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    async def count_enrolled_students(self, section_id: int, search: str | None) -> int:
        query = (
            select(func.count(Student.id))
            .select_from(Student)
            .join(
                Enrollment,
                Enrollment.student_id == Student.id,
            )
            .where(
                Enrollment.course_section_id == section_id,
                Enrollment.is_cancel.is_(False),
                Student.is_cancel.is_(False),
            )
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Student.student_code.ilike(keyword),
                    Student.full_name.ilike(keyword),
                )
            )

        result = await self.db.execute(query)
        return int(result.scalar_one() or 0)

    async def get_student_by_id(self, student_id: int):
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.administrative_class))
            .where(Student.id == student_id, Student.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_student_by_code_ci(self, student_code: str):
        normalized = student_code.strip().lower()
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.administrative_class))
            .where(
                func.lower(Student.student_code) == normalized,
                Student.is_cancel.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_enrollment(
        self,
        student_id: int,
        section_id: int,
        include_cancel: bool = False,
    ):
        query = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_section_id == section_id,
        )

        if not include_cancel:
            query = query.where(Enrollment.is_cancel.is_(False))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_enrollment(self, student_id: int, section_id: int):
        enrollment = Enrollment(
            student_id=student_id,
            course_section_id=section_id,
            is_cancel=False,
        )
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment

    async def restore_enrollment(self, enrollment: Enrollment):
        enrollment.is_cancel = False
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment

    async def soft_delete_enrollment(self, enrollment: Enrollment):
        enrollment.is_cancel = True
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment
