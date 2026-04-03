from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.course import Course
from src.dto.common import PaginationParams
from src.dto.request.course_request import CourseCreateRequest, CourseUpdateRequest


class ICourseService(ABC):

    @abstractmethod
    async def list_courses(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[Course], int]:
        pass

    @abstractmethod
    async def get_by_id(self, course_id: int) -> Course:
        pass

    @abstractmethod
    async def create(self, request: CourseCreateRequest) -> Course:
        pass

    @abstractmethod
    async def update(self, course_id: int, request: CourseUpdateRequest) -> Course:
        pass

    @abstractmethod
    async def delete(self, course_id: int) -> bool:
        pass