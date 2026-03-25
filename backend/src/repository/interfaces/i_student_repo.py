from abc import ABC, abstractmethod
from typing import Any, List, Optional

from src.db.models.administrative_class import AdministrativeClass
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

    @abstractmethod
    async def get_administrative_class_by_id(self, class_id: int) -> Optional[AdministrativeClass]:
        pass

    @abstractmethod
    async def get_all_administrative_classes(self) -> List[AdministrativeClass]:
        pass

    @abstractmethod
    async def get_by_student_code(self, student_code: str) -> Optional[Student]:
        pass

    @abstractmethod
    async def count_faces_by_student_ids(self, student_ids: List[int]) -> dict[int, int]:
        pass

    @abstractmethod
    async def get_existing_student_codes_ci(self, codes: List[str]) -> set[str]:
        pass

    @abstractmethod
    async def bulk_insert(self, rows: List[dict]) -> None:
        pass
