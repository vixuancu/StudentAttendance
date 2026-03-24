"""
StudentController – Lớp điều phối.
"""

import math
from typing import Optional

from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.dto.response.student_response import AdministrativeClassResponse, StudentResponse
from src.services.interfaces.i_student_service import IStudentService


class StudentController:

    def __init__(self, service: IStudentService):
        self.service = service

    @staticmethod
    def _to_response(student) -> StudentResponse:
        administrative_class = student.__dict__.get("administrative_class")
        return StudentResponse(
            id=student.id,
            student_code=student.student_code,
            full_name=student.full_name,
            birth_of_date=student.birth_of_date,
            gender=student.gender,
            administrative_class_id=student.administrative_class_id,
            administrative_class_name=administrative_class.name if administrative_class else None,
            face_count=getattr(student, "face_count", 0),
            is_cancel=student.is_cancel,
            created_at=student.created_at,
            updated_at=student.updated_at,
        )

    async def get_student(self, id: int) -> DataResponse[StudentResponse]:
        student = await self.service.get_by_id(id)
        return DataResponse(
            data=self._to_response(student),
            message="Lấy thông tin sinh viên thành công",
        )

    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        administrative_class_id: Optional[int] = None,
        is_cancel: Optional[bool] = None,
    ) -> ListResponse[StudentResponse]:
        students, total = await self.service.get_students(
            pagination, search, administrative_class_id, is_cancel
        )
        return ListResponse(
            data=[self._to_response(s) for s in students],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def create_student(
        self, request: StudentCreateRequest
    ) -> DataResponse[StudentResponse]:
        student = await self.service.create(request)
        return DataResponse(
            data=self._to_response(student),
            message="Tạo sinh viên thành công",
        )

    async def update_student(
        self, id: int, request: StudentUpdateRequest
    ) -> DataResponse[StudentResponse]:
        student = await self.service.update(id, request)
        return DataResponse(
            data=self._to_response(student),
            message="Cập nhật sinh viên thành công",
        )

    async def delete_student(self, id: int) -> DataResponse:
        await self.service.delete(id)
        return DataResponse(message="Khóa sinh viên thành công")

    async def hard_delete_student(self, id: int) -> DataResponse:
        await self.service.hard_delete(id)
        return DataResponse(message="Xóa sinh viên thành công")

    async def get_administrative_classes(self) -> ListResponse[AdministrativeClassResponse]:
        classes = await self.service.get_administrative_class_options()
        return ListResponse(
            data=[AdministrativeClassResponse.model_validate(item) for item in classes],
            total=len(classes),
            page=1,
            page_size=len(classes),
            total_pages=1,
        )
