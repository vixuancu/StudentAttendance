"""
StudentController – Lớp điều phối mỏng (thin orchestration layer).
Nhiệm vụ:
  ✅ Nhận request từ client
  ✅ Validate input (đã qua Pydantic ở route)
  ✅ Gọi service
  ✅ Map kết quả sang response DTO
  ✅ Xử lý HTTP status code / error

KHÔNG chứa business logic.
"""

import math
from typing import Optional

from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.dto.response.student_response import StudentResponse
from src.services.interfaces.i_student_service import IStudentService


class StudentController:
    """Controller điều phối cho Student – nhận IService qua DI."""
    
# hàm init làm nhiệm vụ khởi tạo đối tượng StudentController với một dịch vụ IStudentService được truyền vào thông qua Dependency Injection (DI).
    def __init__(self, service: IStudentService): 
        self.service = service

    # ------------------------------------------------------------------ #
    #  GET ONE
    # ------------------------------------------------------------------ #

    async def get_student(self, id: int) -> DataResponse[StudentResponse]:
        student = await self.service.get_by_id(id)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Lấy thông tin sinh viên thành công",
        )

    # ------------------------------------------------------------------ #
    #  GET LIST (pagination + search)
    # ------------------------------------------------------------------ #

    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        class_code: Optional[str] = None,
    ) -> ListResponse[StudentResponse]:
        students, total = await self.service.get_students(
            pagination, search, class_code
        )
        return ListResponse(
            data=[StudentResponse.model_validate(s) for s in students],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    # ------------------------------------------------------------------ #
    #  CREATE
    # ------------------------------------------------------------------ #

    async def create_student(
        self, request: StudentCreateRequest
    ) -> DataResponse[StudentResponse]:
        student = await self.service.create(request)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Tạo sinh viên thành công",
        )

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    async def update_student(
        self, id: int, request: StudentUpdateRequest
    ) -> DataResponse[StudentResponse]:
        student = await self.service.update(id, request)
        return DataResponse(
            data=StudentResponse.model_validate(student),
            message="Cập nhật sinh viên thành công",
        )

    # ------------------------------------------------------------------ #
    #  DELETE
    # ------------------------------------------------------------------ #

    async def delete_student(self, id: int) -> DataResponse:
        await self.service.delete(id)
        return DataResponse(message="Xóa sinh viên thành công")
