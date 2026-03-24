"""
StudentService – Business logic thuần cho Student.
KHÔNG import FastAPI/HTTP. Chỉ throw BusinessException.
"""

import logging
from typing import Any, List, Optional, Tuple

from src.db.models.administrative_class import AdministrativeClass
from src.db.models.student import Student
from src.dto.common import PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.services.interfaces.i_student_service import IStudentService
from src.utils.exceptions import AlreadyExistsException, NotFoundException, ValidationException


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
        administrative_class_id: Optional[int] = None,
        is_cancel: Optional[bool] = None,
    ) -> Tuple[List[Student], int]:
        filters: List[Any] = []

        if is_cancel is not None:
            filters.append(Student.is_cancel.is_(is_cancel))

        if search:
            keyword = f"%{search.strip()}%"
            filters.append(
                Student.full_name.ilike(keyword) | Student.student_code.ilike(keyword)
            )
        if administrative_class_id:
            filters.append(Student.administrative_class_id == administrative_class_id)

        total = await self.repo.count(filters=filters)
        students = await self.repo.get_all(
            skip=pagination.offset,
            limit=pagination.limit,
            filters=filters,
        )

        student_ids = [student.id for student in students]
        face_count_map = await self.repo.count_faces_by_student_ids(student_ids)
        for student in students:
            setattr(student, "face_count", face_count_map.get(student.id, 0))

        return students, total

    async def create(self, request: StudentCreateRequest) -> Student:
        student_code = request.student_code.strip()
        existing = await self.repo.get_by_student_code(student_code)
        if existing is not None:
            raise AlreadyExistsException(
                resource="Sinh viên",
                field="student_code",
                value=student_code,
            )

        admin_class = await self.repo.get_administrative_class_by_id(request.administrative_class_id)
        if admin_class is None:
            raise ValidationException("Lớp hành chính không hợp lệ", field="administrative_class_id")

        payload = request.model_dump(exclude_none=True)
        payload["student_code"] = student_code
        created = await self.repo.create(payload)
        refreshed = await self.repo.get_by_id(created.id)
        return refreshed if refreshed is not None else created

    async def update(self, id: int, request: StudentUpdateRequest) -> Student:
        student = await self.get_by_id(id)
        update_data = request.model_dump(exclude_unset=True)

        if "administrative_class_id" in update_data and update_data["administrative_class_id"] is not None:
            admin_class = await self.repo.get_administrative_class_by_id(update_data["administrative_class_id"])
            if admin_class is None:
                raise ValidationException("Lớp hành chính không hợp lệ", field="administrative_class_id")

        updated = await self.repo.update(student, update_data)
        refreshed = await self.repo.get_by_id(updated.id)
        return refreshed if refreshed is not None else updated

    async def delete(self, id: int) -> bool:
        student = await self.get_by_id(id)
        return await self.repo.update(student, {"is_cancel": True})

    async def hard_delete(self, id: int) -> bool:
        student = await self.get_by_id(id)
        return await self.repo.delete(student.id)

    async def get_administrative_class_options(self) -> List[AdministrativeClass]:
        return await self.repo.get_all_administrative_classes()
