from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.classroom import Classroom
from src.dto.common import PaginationParams
from src.dto.request.classroom_request import (
    ClassroomCreateRequest,
    ClassroomUpdateRequest,
)


class IClassroomService(ABC):

    @abstractmethod
    async def get_classrooms(
        self, pagination: PaginationParams, class_name: Optional[str] = None
    ) -> tuple[list[Classroom], int]:
        pass

    @abstractmethod
    async def get_classroom(self, id: int) -> Optional[Classroom]:
        pass

    @abstractmethod
    async def get_available_classrooms(self) -> list[Classroom]:
        pass

    @abstractmethod
    async def create_classroom(self, request: ClassroomCreateRequest) -> Classroom:
        pass

    @abstractmethod
    async def update_classroom(
        self, id: int, request: ClassroomUpdateRequest
    ) -> Classroom:
        pass

    @abstractmethod
    async def delete_classroom(self, id: int) -> Classroom:
        pass
