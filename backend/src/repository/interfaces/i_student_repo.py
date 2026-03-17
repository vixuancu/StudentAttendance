from abc import ABC, abstractmethod
from typing import Any, List, Optional
from src.db.models.student import Student


class IStudentRepository(ABC):

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Student]:
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
    ) -> List[Student]:
        pass

    @abstractmethod
    async def count(self, filters: Optional[List[Any]] = None) -> int:
        pass

    @abstractmethod
    async def create(self, data: dict) -> Student:
        pass

    @abstractmethod
    async def update(self, db_obj: Student, data: dict) -> Student:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass