from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.administrative_class import AdministrativeClass
from src.dto.common import PaginationParams
from src.dto.request.administrative_class_request import (
    AdministrativeClassCreateRequest,
    AdministrativeClassUpdateRequest,
)
from src.dto.response.administrative_class_response import AdministrativeClassStatsResponse


class IAdministrativeClassService(ABC):

    @abstractmethod
    async def list_classes(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[AdministrativeClass], int]:
        pass

    @abstractmethod
    async def get_by_id(self, class_id: int) -> AdministrativeClass:
        pass

    @abstractmethod
    async def create(self, request: AdministrativeClassCreateRequest) -> AdministrativeClass:
        pass

    @abstractmethod
    async def update(self, class_id: int, request: AdministrativeClassUpdateRequest) -> AdministrativeClass:
        pass

    @abstractmethod
    async def lock(self, class_id: int) -> AdministrativeClass:
        pass

    @abstractmethod
    async def unlock(self, class_id: int) -> AdministrativeClass:
        pass

    @abstractmethod
    async def hard_delete(self, class_id: int) -> bool:
        pass

    @abstractmethod
    async def get_stats(self, search: Optional[str] = None) -> AdministrativeClassStatsResponse:
        pass
