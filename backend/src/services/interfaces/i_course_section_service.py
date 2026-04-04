from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.classroom import Classroom
from src.db.models.course import Course
from src.db.models.course_section import CourseSection
from src.db.models.student import Student
from src.db.models.user import User
from src.dto.common import PaginationParams
from src.dto.request.course_section_request import (
    CourseSectionEnrollmentCreateRequest,
    CourseSectionCreateRequest,
    CourseSectionUpdateRequest,
)


class ICourseSectionService(ABC):

    @abstractmethod
    async def list_sections(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[tuple[CourseSection, int]], int]:
        pass

    @abstractmethod
    async def get_by_id(self, section_id: int) -> CourseSection:
        pass

    @abstractmethod
    async def create(self, request: CourseSectionCreateRequest) -> CourseSection:
        pass

    @abstractmethod
    async def update(
        self,
        section_id: int,
        request: CourseSectionUpdateRequest,
    ) -> CourseSection:
        pass

    @abstractmethod
    async def delete(self, section_id: int) -> CourseSection:
        pass

    @abstractmethod
    async def get_form_options(
        self,
    ) -> tuple[list[Course], list[User], list[Classroom]]:
        pass

    @abstractmethod
    async def list_enrolled_students(
        self,
        section_id: int,
        pagination: PaginationParams,
        search: Optional[str] = None,
    ) -> tuple[list[Student], int]:
        pass

    @abstractmethod
    async def add_student_to_section(
        self,
        section_id: int,
        request: CourseSectionEnrollmentCreateRequest,
    ) -> Student:
        pass

    @abstractmethod
    async def remove_student_from_section(
        self, section_id: int, student_id: int
    ) -> None:
        pass
