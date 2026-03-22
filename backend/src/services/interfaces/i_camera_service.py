from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.camera import Camera
from src.dto.common import PaginationParams
from src.dto.request.camera_request import CameraCreateRequest, CameraUpdateRequest


class ICameraService(ABC):

    @abstractmethod
    async def get_cameras(
        self, pagination: PaginationParams, camera_name: Optional[str] = None
    ) -> tuple[list[Camera], int]:
        pass

    @abstractmethod
    async def get_camera(self, id: int) -> Optional[Camera]:
        pass

    @abstractmethod
    async def create_camera(self, request: CameraCreateRequest) -> Camera:
        pass

    @abstractmethod
    async def update_camera(self, id: int, request: CameraUpdateRequest) -> Camera:
        pass

    @abstractmethod
    async def delete_camera(self, id: int) -> Camera:
        pass
