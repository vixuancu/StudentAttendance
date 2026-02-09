"""
Student Routes – Thin layer, chỉ khai báo endpoint.
Mọi logic đều nằm trong Controller → Service.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.controller.student_controller import StudentController
from src.deps import get_student_controller
from src.dto.common import DataResponse, ListResponse
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.dto.response.student_response import StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=ListResponse[StudentResponse])
async def get_students(
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc mã SV"),
    class_code: Optional[str] = Query(None, description="Lọc theo mã lớp"),
    ctrl: StudentController = Depends(get_student_controller),
):
    """Lấy danh sách sinh viên (có pagination + search)"""
    from src.dto.common import PaginationParams

    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.get_students(pagination, search, class_code)


@router.get("/{student_id}", response_model=DataResponse[StudentResponse])
async def get_student(
    student_id: int,
    ctrl: StudentController = Depends(get_student_controller),
):
    """Lấy thông tin sinh viên theo ID"""
    return await ctrl.get_student(student_id)


@router.post(
    "",
    response_model=DataResponse[StudentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_student(
    request: StudentCreateRequest,
    ctrl: StudentController = Depends(get_student_controller),
):
    """Tạo sinh viên mới"""
    return await ctrl.create_student(request)


@router.put("/{student_id}", response_model=DataResponse[StudentResponse])
async def update_student(
    student_id: int,
    request: StudentUpdateRequest,
    ctrl: StudentController = Depends(get_student_controller),
):
    """Cập nhật thông tin sinh viên"""
    return await ctrl.update_student(student_id, request)


@router.delete("/{student_id}", response_model=DataResponse)
async def delete_student(
    student_id: int,
    ctrl: StudentController = Depends(get_student_controller),
):
    """Xóa sinh viên"""
    return await ctrl.delete_student(student_id)
