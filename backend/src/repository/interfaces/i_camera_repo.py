from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.camera import Camera


class ICameraRepository(ABC):

    @abstractmethod
    async def get_cameras(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> list[Camera]:
        pass

    @abstractmethod
    async def get_camera_by_id(self, id: int) -> Optional[Camera]:
        pass

    @abstractmethod
    async def get_camera_by_ip(self, ip: str) -> Optional[Camera]:
        pass

    @abstractmethod
    async def create(self, data: dict) -> Camera:
        pass

    @abstractmethod
    async def delete(self, id: int) -> Optional[Camera]:
        pass

    # @abstractmethod
    # async def get_by_camera_name(self, camera_name: str) -> Optional[Camera]:
    #     """Lấy camera theo camera_name."""
    #     pass

    # @abstractmethod
    # async def get_by_id(self, id: int) -> Optional[Camera]:
    #     """Lấy camera theo ID."""
    #     pass

    # @abstractmethod
    # async def count_users(
    #     self,
    #     search: Optional[str] = None,
    #     role_name: Optional[str] = None,
    # ) -> int:
    #     """Đếm camera có filter."""
    #     pass

    # @abstractmethod
    # async def update(self, db_obj: Camera, data: dict) -> Camera:
    #     """Cập nhật thông tin camera."""
    #     pass
