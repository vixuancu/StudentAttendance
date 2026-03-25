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
    async def get_camera_by_name(self, camera_name: str) -> Optional[Camera]:
        pass

    @abstractmethod
    async def get_camera_by_ip(self, ip: str) -> Optional[Camera]:
        pass

    @abstractmethod
    async def get_active_camera_by_classroom(
        self, classroom_id: int
    ) -> Optional[Camera]:
        pass

    @abstractmethod
    async def delete(self, id: int) -> Optional[Camera]:
        pass
