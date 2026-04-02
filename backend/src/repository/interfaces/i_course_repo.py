from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.course import Course


class ICourseRepository(ABC):

    @abstractmethod
    async def get_by_id(self, course_id: int) -> Optional[Course]:
        pass

    @abstractmethod
    async def get_by_name_ci(self, course_name: str) -> Optional[Course]:
        pass

    @abstractmethod
    async def list_courses(self, skip: int, limit: int, search: str | None, is_cancel: bool | None) -> list[Course]:
        pass

    @abstractmethod
    async def count_courses(self, search: str | None, is_cancel: bool | None) -> int:
        pass

    @abstractmethod
    async def create(self, data: dict) -> Course:
        pass

    @abstractmethod
    async def update(self, db_obj: Course, data: dict) -> Course:
        pass

    @abstractmethod
    async def delete(self, course_id: int) -> bool:
        pass