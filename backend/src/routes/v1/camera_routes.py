from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.controller.camera_controller import CameraController
from src.db.models.user import User
from src.deps import get_camera_controller
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.camera_request import CameraCreateRequest, CameraUpdateRequest
from src.dto.response.camera_response import CameraResponse, CameraDetailResponse
from src.middleware.auth import require_roles

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get(
    "",
    response_model=ListResponse[CameraDetailResponse],
    summary="Lấy danh sách Camera",
)
async def get_cameras(
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    cameraName: Optional[str] = Query(None, description="Tìm theo tên camera"),
    _current_user: User = Depends(require_roles("admin")),
    ctrl: CameraController = Depends(get_camera_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.get_cameras(pagination, camera_name=cameraName)


@router.get(
    "/{id}",
    response_model=DataResponse[CameraDetailResponse],
    summary="Lấy camera theo id",
)
async def get_camera(
    id: int,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: CameraController = Depends(get_camera_controller),
):
    return await ctrl.get_camera(id)


@router.post(
    "", response_model=DataResponse[CameraDetailResponse], summary="Tạo camera"
)
async def create_camera(
    request: CameraCreateRequest,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: CameraController = Depends(get_camera_controller),
):
    return await ctrl.create_camera(request)


@router.put(
    "/{id}", response_model=DataResponse[CameraDetailResponse], summary="Sửa camera"
)
async def update_camera(
    id: int,
    request: CameraUpdateRequest,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: CameraController = Depends(get_camera_controller),
):
    return await ctrl.update_camera(id, request)


@router.delete(
    "/{id}",
    response_model=DataResponse[CameraDetailResponse],
    summary="Xóa camera theo id",
)
async def delete_camera(
    id: int,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: CameraController = Depends(get_camera_controller),
):
    return await ctrl.delete_camera(id)
