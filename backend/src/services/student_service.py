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
from src.utils.exceptions import AlreadyExistsException, NotFoundException


class StudentService(IStudentService):
    logger = logging.getLogger(__name__)
    """
    Concrete implementation của IStudentService.
    Nhận IStudentRepository qua DI – không tự tạo repo.
    """

    def __init__(self, repo: IStudentRepository):
        self.repo = repo

    # ------------------------------------------------------------------ #
    #  READ
    # ------------------------------------------------------------------ #

    async def get_by_id(self, id: int) -> Student:
        student = await self.repo.get_by_id(id)
        if not student:
            raise NotFoundException(resource="Sinh viên", identifier=id)
        return student

    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        class_code: Optional[str] = None,
    ) -> Tuple[List[Student], int]:
        """Trả về (danh sách student, total_count) để controller tính pagination."""

        # Xây dựng điều kiện filter
        filters: List[Any] = []
        if search:
            filters.append(
                Student.full_name.ilike(f"%{search}%")
                | Student.student_code.ilike(f"%{search}%")
            )
        if class_code:
            filters.append(Student.class_code == class_code)

        total = await self.repo.count(filters=filters if filters else None)
        students = await self.repo.get_all(
            skip=pagination.offset,
            limit=pagination.limit,
            filters=filters if filters else None,
        )
        self.logger.info("test logging")
        return students, total

    # ------------------------------------------------------------------ #
    #  CREATE
    # ------------------------------------------------------------------ #

    async def create(self, request: StudentCreateRequest) -> Student:
        existing = await self.repo.get_by_student_code(request.student_code)
        if existing:
            raise AlreadyExistsException(
                resource="Sinh viên",
                field="student_code",
                value=request.student_code,
            )
        return await self.repo.create(request.model_dump())

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    async def update(self, id: int, request: StudentUpdateRequest) -> Student:
        student = await self.get_by_id(id)  # raise nếu không tìm thấy
        update_data = request.model_dump(exclude_unset=True)
        return await self.repo.update(student, update_data)

    # ------------------------------------------------------------------ #
    #  DELETE
    # ------------------------------------------------------------------ #

    async def delete(self, id: int) -> bool:
        await self.get_by_id(id)  # raise nếu không tìm thấy
        return await self.repo.delete(id)