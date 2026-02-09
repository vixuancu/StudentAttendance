from typing import Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.student import Student
from src.repository.base import BaseRepository
from src.repository.interfaces.i_student_repo import IStudentRepository


class StudentRepository(BaseRepository, IStudentRepository):
    """
    Concrete implementation của IStudentRepository.
    Kế thừa BaseRepository để tận dụng generic CRUD,
    implement IStudentRepository để đảm bảo contract.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)

    # --- Các method đặc thù cho Student ---

    async def get_by_student_code(self, code: str) -> Optional[Student]:
        """Lấy sinh viên theo mã sinh viên"""
        result = await self.db.execute(
            select(Student).where(Student.student_code == code)
        )
        return result.scalar_one_or_none()