from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.classroom import Classroom


class IClassroomRepository(ABC):

    @abstractmethod
    async def get_classrooms(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Classroom]:
        pass

    @abstractmethod
    async def get_classroom_by_id(self, id: int) -> Optional[Classroom]:
        pass

    @abstractmethod
    async def get_classroom_by_name(self, id: int) -> Optional[Classroom]:
        pass

    @abstractmethod
    async def create_classroom(self, data: dict) -> Classroom:
        pass

    @abstractmethod
    async def get_classrooms_without_camera(self) -> list[Classroom]:
        pass

    @abstractmethod
    async def delete(self, id: int) -> Optional[Classroom]:
        pass
