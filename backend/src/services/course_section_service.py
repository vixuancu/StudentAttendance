from datetime import datetime
from typing import Optional

from src.constant.error_code import ERROR_CODES
from src.db.models.course_section import CourseSection
from src.dto.common import PaginationParams
from src.dto.request.course_section_request import (
    CourseSectionCreateRequest,
    CourseSectionUpdateRequest,
)
from src.repository.interfaces.i_course_section_repo import ICourseSectionRepository
from src.services.interfaces.i_course_section_service import ICourseSectionService
from src.utils.exception import AlreadyExists, NotFound, Validation


class CourseSectionService(ICourseSectionService):

    def __init__(self, repo: ICourseSectionRepository):
        self.repo = repo

    async def list_sections(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[tuple[CourseSection, int]], int]:
        items = await self.repo.list_sections(
            skip=pagination.offset,
            limit=pagination.limit,
            search=search,
            is_cancel=is_cancel,
        )
        total = await self.repo.count_sections(search=search, is_cancel=is_cancel)
        return items, total

    async def get_by_id(self, section_id: int) -> CourseSection:
        item = await self.repo.get_by_id(section_id)
        if item is None:
            raise NotFound(ERROR_CODES.COURSE_SECTION.COURSE_SECTION_NOT_FOUND)
        return item

    async def _validate_foreign_keys(
        self,
        course_id: Optional[int],
        user_id: Optional[int],
        room_id: Optional[int],
    ):
        if course_id is not None:
            course = await self.repo.get_course_by_id(course_id)
            if course is None:
                raise NotFound(ERROR_CODES.COURSE.COURSE_NOT_FOUND)

        if user_id is not None:
            lecturer = await self.repo.get_lecturer_by_id(user_id)
            if lecturer is None:
                raise NotFound(ERROR_CODES.COURSE_SECTION.LECTURER_NOT_FOUND)

        if room_id is not None:
            room = await self.repo.get_room_by_id(room_id)
            if room is None:
                raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)

    @staticmethod
    def _validate_time_fields(
        start_date: datetime,
        end_date: datetime,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
    ):
        if start_date >= end_date:
            raise Validation(
                message="Ngày bắt đầu phải nhỏ hơn ngày kết thúc",
                error_code=ERROR_CODES.COURSE_SECTION.INVALID_DATE_RANGE,
            )

        if start_time is not None and end_time is not None and start_time >= end_time:
            raise Validation(
                message="Giờ bắt đầu phải nhỏ hơn giờ kết thúc",
                error_code=ERROR_CODES.COURSE_SECTION.INVALID_TIME_RANGE,
            )

    async def create(self, request: CourseSectionCreateRequest) -> CourseSection:
        normalized_name = request.name.strip()
        existed = await self.repo.get_by_name_ci(normalized_name)
        if existed is not None:
            raise AlreadyExists(
                ERROR_CODES.COURSE_SECTION.COURSE_SECTION_NAME_IS_EXISTED
            )

        await self._validate_foreign_keys(
            course_id=request.course_id,
            user_id=request.user_id,
            room_id=request.room_id,
        )

        self._validate_time_fields(
            start_date=request.start_date,
            end_date=request.end_date,
            start_time=request.start_time,
            end_time=request.end_time,
        )

        data = request.model_dump()
        data["name"] = normalized_name
        data["is_cancel"] = False

        created = await self.repo.create(data)
        refreshed = await self.repo.get_by_id(created.id)
        return refreshed if refreshed is not None else created

    async def update(
        self,
        section_id: int,
        request: CourseSectionUpdateRequest,
    ) -> CourseSection:
        item = await self.get_by_id(section_id)
        data = request.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            normalized_name = data["name"].strip()
            existed = await self.repo.get_by_name_ci(normalized_name)
            if existed is not None and existed.id != item.id:
                raise AlreadyExists(
                    ERROR_CODES.COURSE_SECTION.COURSE_SECTION_NAME_IS_EXISTED
                )
            data["name"] = normalized_name

        await self._validate_foreign_keys(
            course_id=data.get("course_id"),
            user_id=data.get("user_id"),
            room_id=data.get("room_id"),
        )

        start_date = data.get("start_date", item.start_date)
        end_date = data.get("end_date", item.end_date)
        start_time = data.get("start_time", item.start_time)
        end_time = data.get("end_time", item.end_time)
        self._validate_time_fields(start_date, end_date, start_time, end_time)

        updated = await self.repo.update(item, data)
        refreshed = await self.repo.get_by_id(updated.id)
        return refreshed if refreshed is not None else updated

    async def delete(self, section_id: int) -> CourseSection:
        item = await self.get_by_id(section_id)
        return await self.repo.soft_delete(item)

    async def get_form_options(self):
        courses = await self.repo.list_course_options()
        lecturers = await self.repo.list_lecturer_options()
        rooms = await self.repo.list_room_options()
        return courses, lecturers, rooms
