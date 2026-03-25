"""
Student Routes
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from src.controller.student_controller import StudentController
from src.controller.student_face_controller import StudentFaceController
from src.db.models.user import User
from src.deps import get_student_controller, get_student_face_controller
from src.dto.common import DataResponse, ListResponse
from src.dto.request.student_face_request import StudentFaceCreateRequest
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest
from src.dto.response.student_face_response import StudentFaceResponse
from src.dto.response.student_response import (
    AdministrativeClassResponse,
    StudentImportResultResponse,
    StudentStatsResponse,
    StudentResponse,
)
from src.middleware.auth import require_roles

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/import/template")
async def download_import_template(
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    content = ctrl.service.build_import_template()
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="student_import_template.xlsx"',
        },
    )


@router.post("/import", response_model=DataResponse[StudentImportResultResponse])
async def import_students(
    file: UploadFile = File(..., description="File Excel .xlsx"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    content = await file.read()
    return await ctrl.import_students(file_content=content, filename=file.filename)


@router.get("", response_model=ListResponse[StudentResponse])
async def get_students(
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc mã sinh viên"),
    administrative_class_id: Optional[int] = Query(None, description="Lọc theo lớp hành chính"),
    is_cancel: Optional[bool] = Query(None, description="Lọc theo trạng thái khóa"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    from src.dto.common import PaginationParams
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.get_students(pagination, search, administrative_class_id, is_cancel)


@router.get("/stats", response_model=DataResponse[StudentStatsResponse])
async def get_student_stats(
    search: Optional[str] = Query(None, description="Tìm theo tên hoặc mã sinh viên"),
    administrative_class_id: Optional[int] = Query(None, description="Lọc theo lớp hành chính"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    return await ctrl.get_student_stats(search=search, administrative_class_id=administrative_class_id)


@router.get("/administrative-classes", response_model=ListResponse[AdministrativeClassResponse])
async def get_administrative_classes(
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    return await ctrl.get_administrative_classes()


@router.get("/{student_id}", response_model=DataResponse[StudentResponse])
async def get_student(
    student_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    return await ctrl.get_student(student_id)


@router.post(
    "",
    response_model=DataResponse[StudentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_student(
    request: StudentCreateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    return await ctrl.create_student(request)


@router.patch("/{student_id}", response_model=DataResponse[StudentResponse])
async def update_student(
    student_id: int,
    request: StudentUpdateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    return await ctrl.update_student(student_id, request)


@router.delete("/{student_id}", response_model=DataResponse)
async def delete_student(
    student_id: int,
    hard: bool = Query(False, description="true để xóa cứng"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentController = Depends(get_student_controller),
):
    if hard:
        return await ctrl.hard_delete_student(student_id)
    return await ctrl.delete_student(student_id)


@router.get("/{student_id}/faces", response_model=ListResponse[StudentFaceResponse])
async def get_student_faces(
    student_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentFaceController = Depends(get_student_face_controller),
):
    return await ctrl.get_faces(student_id)


@router.post("/{student_id}/faces", response_model=DataResponse[StudentFaceResponse])
async def add_student_face(
    student_id: int,
    request: StudentFaceCreateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentFaceController = Depends(get_student_face_controller),
):
    return await ctrl.add_face(student_id, request)


@router.delete("/{student_id}/faces/{face_id}", response_model=DataResponse[None])
async def delete_student_face(
    student_id: int,
    face_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: StudentFaceController = Depends(get_student_face_controller),
):
    return await ctrl.delete_face(student_id, face_id)
