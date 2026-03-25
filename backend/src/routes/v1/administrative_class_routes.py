from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.controller.administrative_class_controller import AdministrativeClassController
from src.db.models.user import User
from src.deps import get_administrative_class_controller
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.administrative_class_request import (
    AdministrativeClassCreateRequest,
    AdministrativeClassUpdateRequest,
)
from src.dto.response.administrative_class_response import (
    AdministrativeClassItemResponse,
    AdministrativeClassStatsResponse,
)
from src.middleware.auth import require_roles

router = APIRouter(prefix="/administrative-classes", tags=["Administrative Classes"])


@router.get("", response_model=ListResponse[AdministrativeClassItemResponse])
async def get_classes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, description="Tìm theo tên lớp"),
    is_cancel: Optional[bool] = Query(None, description="Lọc theo trạng thái khóa"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.list_classes(pagination=pagination, search=search, is_cancel=is_cancel)


@router.get("/stats", response_model=DataResponse[AdministrativeClassStatsResponse])
async def get_stats(
    search: Optional[str] = Query(None, description="Tìm theo tên lớp"),
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    return await ctrl.get_stats(search=search)


@router.get("/{class_id}", response_model=DataResponse[AdministrativeClassItemResponse])
async def get_class(
    class_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    return await ctrl.get_class(class_id)


@router.post("", response_model=DataResponse[AdministrativeClassItemResponse], status_code=status.HTTP_201_CREATED)
async def create_class(
    request: AdministrativeClassCreateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    return await ctrl.create_class(request)


@router.patch("/{class_id}", response_model=DataResponse[AdministrativeClassItemResponse])
async def update_class(
    class_id: int,
    request: AdministrativeClassUpdateRequest,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    return await ctrl.update_class(class_id, request)


@router.delete("/{class_id}", response_model=DataResponse[AdministrativeClassItemResponse])
async def lock_class(
    class_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    return await ctrl.lock_class(class_id)


@router.post("/{class_id}/unlock", response_model=DataResponse[AdministrativeClassItemResponse])
async def unlock_class(
    class_id: int,
    _current_user: User = Depends(require_roles("admin", "giao_vu")),
    ctrl: AdministrativeClassController = Depends(get_administrative_class_controller),
):
    return await ctrl.unlock_class(class_id)
