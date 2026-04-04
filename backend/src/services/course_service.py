from typing import Optional

from src.constant.error_code import ERROR_CODES
from src.db.models.course import Course
from src.dto.common import PaginationParams
from src.dto.request.course_request import CourseCreateRequest, CourseUpdateRequest
from src.repository.interfaces.i_course_repo import ICourseRepository
from src.services.interfaces.i_course_service import ICourseService
from src.utils.exception import AlreadyExists, NotFound


class CourseService(ICourseService):

    def __init__(self, repo: ICourseRepository):
        self.repo = repo

    @staticmethod
    def _normalize_course_name(course_name: str) -> str:
        return " ".join(course_name.split())

    async def list_courses(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[Course], int]:
        items = await self.repo.list_courses(
            skip=pagination.offset,
            limit=pagination.limit,
            search=search,
            is_cancel=is_cancel,
        )
        total = await self.repo.count_courses(search=search, is_cancel=is_cancel)
        return items, total

    async def get_by_id(self, course_id: int) -> Course:
        item = await self.repo.get_by_id(course_id)
        if item is None:
            raise NotFound(ERROR_CODES.COURSE.COURSE_NOT_FOUND)
        return item

    async def create(self, request: CourseCreateRequest) -> Course:
        course_name = self._normalize_course_name(request.course_name)
        existed = await self.repo.get_by_name_ci(course_name)
        if existed is not None:
            raise AlreadyExists(ERROR_CODES.COURSE.COURSE_NAME_IS_EXISTED)

        return await self.repo.create({"course_name": course_name, "is_cancel": False})

    async def update(self, course_id: int, request: CourseUpdateRequest) -> Course:
        item = await self.get_by_id(course_id)
        data = request.model_dump(exclude_unset=True)

        new_name = data.get("course_name")
        if new_name is not None:
            normalized_name = self._normalize_course_name(new_name)
            if not normalized_name:
                raise ValueError("course_name cannot be empty")

            existed = await self.repo.get_by_name_ci(normalized_name)
            if existed is not None and existed.id != item.id:
                raise AlreadyExists(ERROR_CODES.COURSE.COURSE_NAME_IS_EXISTED)

            data["course_name"] = normalized_name

        return await self.repo.update(item, data)

    async def delete(self, course_id: int) -> bool:
        item = await self.get_by_id(course_id)
        return await self.repo.delete(item.id)
