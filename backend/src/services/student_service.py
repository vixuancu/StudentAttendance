"""
StudentService – Business logic thuần cho Student.
KHÔNG import FastAPI/HTTP. Chỉ throw BusinessException.
"""

import logging
from typing import Any, List, Optional, Tuple

from src.db.models.student import Student
from src.dto.common import PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.services.interfaces.i_student_service import IStudentService
from src.utils.exceptions import NotFoundException


class StudentService(IStudentService):
    logger = logging.getLogger(__name__)

    def __init__(self, repo: IStudentRepository):
        self.repo = repo

    async def get_by_id(self, id: int) -> Student:
        student = await self.repo.get_by_id(id)
        if not student:
            raise NotFoundException(resource="Sinh viên", identifier=id)
        return student

    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        administrative_class: Optional[str] = None,
    ) -> Tuple[List[Student], int]:
        filters: List[Any] = []
        # Soft delete filter
        filters.append(Student.is_cancel.is_(False))

        if search:
            filters.append(Student.full_name.ilike(f"%{search}%"))
        if administrative_class:
            filters.append(Student.administrative_class == administrative_class)

        total = await self.repo.count(filters=filters)
        students = await self.repo.get_all(
            skip=pagination.offset,
            limit=pagination.limit,
            filters=filters,
        )
        return students, total

    async def create(self, request: StudentCreateRequest) -> Student:
        return await self.repo.create(request.model_dump(exclude_none=True))

    async def update(self, id: int, request: StudentUpdateRequest) -> Student:
        student = await self.get_by_id(id)
        update_data = request.model_dump(exclude_unset=True)
        return await self.repo.update(student, update_data)

    async def delete(self, id: int) -> bool:
        student = await self.get_by_id(id)
        # Soft delete
        return await self.repo.update(student, {"is_cancel": True})
