from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.controller.course_controller import CourseController
from src.db.models.user import User
from src.deps import get_course_controller
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.course_request import CourseCreateRequest, CourseUpdateRequest
from src.dto.response.course_response import CourseResponse
from src.middleware.auth import require_roles

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=ListResponse[CourseResponse])
async def get_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Tìm theo tên khóa học"),
    is_cancel: Optional[bool] = Query(None, description="Lọc theo trạng thái khóa học"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseController = Depends(get_course_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.list_courses(pagination, search, is_cancel)


@router.get("/{course_id}", response_model=DataResponse[CourseResponse])
async def get_course(
    course_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseController = Depends(get_course_controller),
):
    return await ctrl.get_by_id(course_id)


@router.post("", response_model=DataResponse[CourseResponse], status_code=status.HTTP_201_CREATED)
async def create_course(
    request: CourseCreateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseController = Depends(get_course_controller),
):
    return await ctrl.create(request)


@router.patch("/{course_id}", response_model=DataResponse[CourseResponse])
async def update_course(
    course_id: int,
    request: CourseUpdateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseController = Depends(get_course_controller),
):
    return await ctrl.update(course_id, request)


@router.delete("/{course_id}", response_model=DataResponse[None])
async def delete_course(
    course_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: CourseController = Depends(get_course_controller),
):
    return await ctrl.delete(course_id)