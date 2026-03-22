import logging
from typing import Optional

from src.db.models.camera import Camera
from src.dto.common import PaginationParams
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest
from src.repository.interfaces.i_camera_repo import ICameraRepository
from src.services.interfaces.i_camera_service import ICameraService
from src.utils.exceptions import (
    AlreadyExistsException,
    NotFoundException,
    ValidationException,
)
from src.utils.exception import NotFound, AlreadyExists
from src.utils.security import hash_password
from src.constant.error_code import ERROR_CODES


class CameraService(ICameraService):
    logger = logging.getLogger(__name__)

    def __init__(self, camera_repo: ICameraRepository):
        self.camera_repo = camera_repo

    async def get_cameras(
        self, pagination: PaginationParams, camera_name: Optional[str] = None
    ) -> tuple[list[Camera], int]:
        cameras, total = await self.camera_repo.get_cameras(
            skip=pagination.offset, limit=pagination.limit, camera_name=camera_name
        )

        return cameras, total

    async def get_camera(self, id: int) -> Optional[Camera]:
        camera = await self.camera_repo.get_camera_by_id(id)

        if not camera:
            raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

        return camera

    async def create_camera(self, request) -> Camera:
        try:
            data = request.model_dump()

            exist = await self.camera_repo.get_camera_by_ip(data["ip_address"])

            if exist:
                raise AlreadyExists(ERROR_CODES.CAMERA.IP_ADDRESS_IS_EXISTED)

            camera = await self.camera_repo.create(data)
            return camera
        except Exception as e:
            raise e

    async def update_camera(self, id, request) -> Camera:
        try:
            camera = await self.camera_repo.get_camera_by_id(id)

            if not camera:
                raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

            data = request.model_dump(exclude_unset=True)

            new_ip = data.get("ip_address")
            if new_ip and new_ip != camera.ip_address:
                existing_camera = await self.camera_repo.get_camera_by_ip(new_ip)
                if existing_camera:
                    raise AlreadyExists(ERROR_CODES.CAMERA.IP_ADDRESS_IS_EXISTED)

                data = request.model_dump(exclude_unset=True)
                for key, value in data.items():
                    setattr(camera, key, value)

            await self.camera_repo.db.commit()
            await self.camera_repo.db.refresh(camera)

            return camera
        except Exception as e:
            raise e

    async def delete_camera(self, id: int) -> Camera:
        try:
            camera = await self.camera_repo.delete(id)

            if not camera:
                raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

            return camera
        except Exception as e:
            raise e
