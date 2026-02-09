from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple
from src.db.models.student import Student


class IStudentRepository(ABC):
    """Interface cho StudentRepository"""

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Student]:
        """Lấy sinh viên theo ID"""
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List[Any]] = None,
    ) -> List[Student]:
        """Lấy danh sách sinh viên với pagination và filter"""
        pass

    @abstractmethod
    async def count(self, filters: Optional[List[Any]] = None) -> int:
        """Đếm tổng số bản ghi (có filter)"""
        pass

    @abstractmethod
    async def create(self, data: dict) -> Student:
        """Tạo sinh viên mới"""
        pass

    @abstractmethod
    async def update(self, db_obj: Student, data: dict) -> Student:
        """Cập nhật thông tin sinh viên"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Xóa sinh viên theo ID"""
        pass

    @abstractmethod
    async def get_by_student_code(self, code: str) -> Optional[Student]:
        """Lấy sinh viên theo mã sinh viên"""
        pass