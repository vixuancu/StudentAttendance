from abc import ABC, abstractmethod
from typing import Optional, Tuple, List

from src.db.models.administrative_class import AdministrativeClass
from src.db.models.student import Student
from src.dto.common import PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest


class IStudentService(ABC):

    @abstractmethod
    async def get_by_id(self, id: int) -> Student:
        pass

    @abstractmethod
    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        administrative_class_id: Optional[int] = None,
        is_cancel: Optional[bool] = None,
    ) -> Tuple[List[Student], int]:
        pass

    @abstractmethod
    async def create(self, request: StudentCreateRequest) -> Student:
        pass

    @abstractmethod
    async def update(self, id: int, request: StudentUpdateRequest) -> Student:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass

    @abstractmethod
    async def get_administrative_class_options(self) -> List[AdministrativeClass]:
        pass

    @abstractmethod
    async def hard_delete(self, id: int) -> bool:
        pass
