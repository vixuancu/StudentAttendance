from abc import ABC, abstractmethod
from typing import Optional, Tuple, List

from src.db.models.student import Student
from src.dto.common import PaginationParams
from src.dto.request.student_request import StudentCreateRequest, StudentUpdateRequest


class IStudentService(ABC):
    """Interface cho StudentService - chỉ chứa business logic"""

    @abstractmethod
    async def get_by_id(self, id: int) -> Student:
        """Lấy sinh viên theo ID. Raise NotFoundException nếu không tìm thấy."""
        pass

    @abstractmethod
    async def get_students(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        class_code: Optional[str] = None,
    ) -> Tuple[List[Student], int]:
        """Lấy danh sách sinh viên. Trả về (list, total_count)."""
        pass

    @abstractmethod
    async def create(self, request: StudentCreateRequest) -> Student:
        """Tạo sinh viên mới. Raise AlreadyExistsException nếu trùng mã."""
        pass

    @abstractmethod
    async def update(self, id: int, request: StudentUpdateRequest) -> Student:
        """Cập nhật sinh viên. Raise NotFoundException nếu không tìm thấy."""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Xóa sinh viên. Raise NotFoundException nếu không tìm thấy."""
        pass