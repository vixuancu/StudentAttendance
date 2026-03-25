from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.administrative_class import AdministrativeClass


class IAdministrativeClassRepository(ABC):

    @abstractmethod
    async def get_by_id(self, class_id: int) -> Optional[AdministrativeClass]:
        pass

    @abstractmethod
    async def get_by_name_ci(self, name: str) -> Optional[AdministrativeClass]:
        pass

    @abstractmethod
    async def list_classes(
        self,
        skip: int,
        limit: int,
        search: str | None,
        is_cancel: bool | None,
    ) -> list[AdministrativeClass]:
        pass

    @abstractmethod
    async def count_classes(self, search: str | None, is_cancel: bool | None) -> int:
        pass

    @abstractmethod
    async def create(self, data: dict) -> AdministrativeClass:
        pass

    @abstractmethod
    async def update(self, db_obj: AdministrativeClass, data: dict) -> AdministrativeClass:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass

    @abstractmethod
    async def count_students_by_class_ids(self, class_ids: list[int]) -> dict[int, int]:
        pass

    @abstractmethod
    async def count_students_by_class_id(self, class_id: int) -> int:
        pass
