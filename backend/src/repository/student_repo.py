from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.student import Student
from src.repository.base import BaseRepository
from src.repository.interfaces.i_student_repo import IStudentRepository


class StudentRepository(BaseRepository, IStudentRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)