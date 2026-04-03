from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.classroom import Classroom
from src.db.models.course import Course
from src.db.models.course_section import CourseSection
from src.db.models.user import User


class ICourseSectionRepository(ABC):

    @abstractmethod
    async def get_by_id(self, section_id: int) -> Optional[CourseSection]:
        pass

    @abstractmethod
    async def get_by_name_ci(self, name: str) -> Optional[CourseSection]:
        pass

    @abstractmethod
    async def list_sections(
        self,
        skip: int,
        limit: int,
        search: str | None,
        is_cancel: bool | None,
    ) -> list[tuple[CourseSection, int]]:
        pass

    @abstractmethod
    async def count_sections(self, search: str | None, is_cancel: bool | None) -> int:
        pass

    @abstractmethod
    async def get_course_by_id(self, course_id: int) -> Optional[Course]:
        pass

    @abstractmethod
    async def get_room_by_id(self, room_id: int) -> Optional[Classroom]:
        pass

    @abstractmethod
    async def get_lecturer_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def list_course_options(self) -> list[Course]:
        pass

    @abstractmethod
    async def list_room_options(self) -> list[Classroom]:
        pass

    @abstractmethod
    async def list_lecturer_options(self) -> list[User]:
        pass

    @abstractmethod
    async def create(self, data: dict) -> CourseSection:
        pass

    @abstractmethod
    async def update(self, db_obj: CourseSection, data: dict) -> CourseSection:
        pass

    @abstractmethod
    async def soft_delete(self, db_obj: CourseSection) -> CourseSection:
        pass
