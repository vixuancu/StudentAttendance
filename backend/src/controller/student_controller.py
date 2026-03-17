"""
StudentController – Lớp điều phối.
"""

import math
from typing import Optional

from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.dto.response.student_response import StudentResponse
from src.services.interfaces.i_student_service import IStudentService


class StudentController:

    def __init__(self, service: IStudentService):
        self.service = service

    async def get_student(self, id: int) -> DataResponse[StudentResponse]:
        student = await self.service.get_by_id(id)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Lấy thông tin sinh viên thành công",
        )

    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        administrative_class: Optional[str] = None,
    ) -> ListResponse[StudentResponse]:
        students, total = await self.service.get_students(
            pagination, search, administrative_class
        )
        return ListResponse(
            data=[StudentResponse.model_validate(s) for s in students],
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
            data=StudentResponse.model_validate(student),
            message="Tạo sinh viên thành công",
        )

    async def update_student(
        self, id: int, request: StudentUpdateRequest
    ) -> DataResponse[StudentResponse]:
        student = await self.service.update(id, request)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Cập nhật sinh viên thành công",
        )

    async def delete_student(self, id: int) -> DataResponse:
        await self.service.delete(id)
        return DataResponse(message="Xóa sinh viên thành công")
