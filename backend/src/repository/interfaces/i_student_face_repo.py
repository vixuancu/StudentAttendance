from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.student_face import StudentFace


class IStudentFaceRepository(ABC):

    @abstractmethod
    async def get_by_id(self, face_id: int) -> Optional[StudentFace]:
        pass

    @abstractmethod
    async def get_by_student_id(self, student_id: int) -> list[StudentFace]:
        pass

    @abstractmethod
    async def create(self, data: dict) -> StudentFace:
        pass

    @abstractmethod
    async def delete(self, face_id: int) -> bool:
        pass
