import math
from typing import Optional

from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest
from src.dto.request.camera_request import CameraCreateRequest, CameraUpdateRequest
from src.dto.response.account_response import AccountResponse
from src.dto.response.camera_response import CameraResponse
from src.services.interfaces.i_camera_service import ICameraService


class CameraController:

    def __init__(self, service: ICameraService):
        self.service = service

    async def get_cameras(
        self, pagination: PaginationParams, camera_name: Optional[str] = None
    ) -> ListResponse[CameraResponse]:
        cameras, total = await self.service.get_cameras(
            pagination=pagination, camera_name=camera_name
        )

        return ListResponse(
            data=[CameraResponse.model_validate(camera) for camera in cameras],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def get_camera(self, id: int) -> DataResponse[CameraResponse]:
        camera = await self.service.get_camera(id)

        return DataResponse(
            data=CameraResponse.model_validate(camera),
            message="Lấy thông tin tài khoản thành công",
        )

    async def create_camera(
        self, request: CameraCreateRequest
    ) -> DataResponse[CameraResponse]:
        camera = await self.service.create_camera(request)

        return DataResponse(
            data=CameraResponse.model_validate(camera),
            message="Thêm camera thành công",
        )

    async def update_camera(
        self, id: int, request: CameraUpdateRequest
    ) -> DataResponse[CameraResponse]:
        camera = await self.service.update_camera(id, request)

        return DataResponse(
            data=CameraResponse.model_validate(camera),
            message="Cập nhật camera thành công",
        )

    async def delete_camera(self, id: int) -> DataResponse[CameraResponse]:
        camera = await self.service.delete_camera(id)

        return DataResponse(
            data=CameraResponse.model_validate(camera), message="Xóa camera thành công"
        )
