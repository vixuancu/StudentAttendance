from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from src.controller.course_section_controller import CourseSectionController
from src.db.models.user import User
from src.deps import get_course_section_controller
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.course_section_request import (
    CourseSectionEnrollmentCreateRequest,
    CourseSectionCreateRequest,
    CourseSectionUpdateRequest,
)
from src.dto.response.course_section_response import (
    CourseSectionFormOptionsResponse,
    CourseSectionResponse,
)
from src.dto.response.student_response import StudentResponse
from src.dto.response.student_response import StudentImportResultResponse
from src.middleware.auth import require_roles

router = APIRouter(prefix="/course-sections", tags=["Course Sections"])


@router.get("", response_model=ListResponse[CourseSectionResponse])
async def get_course_sections(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(
        None, description="Tìm theo mã lớp, học phần, giảng viên"
    ),
    is_cancel: Optional[bool] = Query(None, description="Lọc theo trạng thái hủy"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.list_sections(pagination, search, is_cancel)


@router.get("/options", response_model=DataResponse[CourseSectionFormOptionsResponse])
async def get_course_section_options(
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.get_form_options()


@router.get("/{section_id}", response_model=DataResponse[CourseSectionResponse])
async def get_course_section(
    section_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.get_by_id(section_id)


@router.post(
    "",
    response_model=DataResponse[CourseSectionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_course_section(
    request: CourseSectionCreateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.create(request)


@router.patch("/{section_id}", response_model=DataResponse[CourseSectionResponse])
async def update_course_section(
    section_id: int,
    request: CourseSectionUpdateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.update(section_id, request)


@router.delete("/{section_id}", response_model=DataResponse[None])
async def delete_course_section(
    section_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.delete(section_id)


@router.get("/{section_id}/students", response_model=ListResponse[StudentResponse])
async def get_course_section_students(
    section_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Tìm theo mã/tên sinh viên"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.list_section_students(section_id, pagination, search)


@router.post(
    "/{section_id}/students",
    response_model=DataResponse[StudentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_student_to_course_section(
    section_id: int,
    request: CourseSectionEnrollmentCreateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.add_student_to_section(section_id, request)


@router.get("/{section_id}/students/import/template")
async def download_section_student_import_template(
    section_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    content = await ctrl.download_student_import_template(section_id)
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="credit_class_student_import_template.xlsx"',
        },
    )


@router.post(
    "/{section_id}/students/import",
    response_model=DataResponse[StudentImportResultResponse],
)
async def import_students_to_course_section(
    section_id: int,
    file: UploadFile = File(..., description="File Excel .xlsx"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    content = await file.read()
    return await ctrl.import_students_to_section(
        section_id=section_id,
        file_content=content,
        filename=file.filename,
    )


@router.delete("/{section_id}/students/{student_id}", response_model=DataResponse[None])
async def remove_student_from_course_section(
    section_id: int,
    student_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseSectionController = Depends(get_course_section_controller),
):
    return await ctrl.remove_student_from_section(section_id, student_id)
