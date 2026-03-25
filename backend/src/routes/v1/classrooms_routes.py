from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.controller.classroom_controller import ClassroomController
from src.db.models.user import User
from src.deps import get_classroom_controller
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.classroom_request import (
    ClassroomCreateRequest,
    ClassroomUpdateRequest,
)
from src.dto.response.classroom_response import ClassroomResponse
from src.middleware.auth import require_roles

router = APIRouter(prefix="/classrooms", tags=["Classrooms"])


@router.get(
    "",
    response_model=ListResponse[ClassroomResponse],
    summary="Lấy danh sách phòng học",
)
async def get_classrooms(
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    camera_name: Optional[str] = Query(None, description="Tìm theo tên camera"),
    _current_user: User = Depends(require_roles("admin")),
    ctrl: ClassroomController = Depends(get_classroom_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.get_classrooms(pagination, camera_name)


@router.get(
    "/available",
    response_model=DataResponse[list[ClassroomResponse]],
    summary="Lấy danh sách phòng học chưa được gán camera",
)
async def get_available_classrooms(
    _current_user: User = Depends(require_roles("admin")),
    ctrl: ClassroomController = Depends(get_classroom_controller),
):
    return await ctrl.get_available_classrooms()


@router.get(
    "/{id}",
    response_model=DataResponse[ClassroomResponse],
    summary="Lấy phòng học theo id",
)
async def get_classroom(
    id: int,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: ClassroomController = Depends(get_classroom_controller),
):
    return await ctrl.get_classroom(id)


@router.post(
    "", response_model=DataResponse[ClassroomResponse], summary="Tạo phòng học"
)
async def create_classroom(
    request: ClassroomCreateRequest,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: ClassroomController = Depends(get_classroom_controller),
):
    return await ctrl.create_classroom(request)


@router.put(
    "/{id}", response_model=DataResponse[ClassroomResponse], summary="Sửa phòng học"
)
async def update_classroom(
    id: int,
    request: ClassroomUpdateRequest,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: ClassroomController = Depends(get_classroom_controller),
):
    return await ctrl.update_classroom(id, request)


@router.delete(
    "/{id}",
    response_model=DataResponse[ClassroomResponse],
    summary="Xóa phòng học theo id",
)
async def delete_classroom(
    id: int,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: ClassroomController = Depends(get_classroom_controller),
):
    return await ctrl.delete_classroom(id)
