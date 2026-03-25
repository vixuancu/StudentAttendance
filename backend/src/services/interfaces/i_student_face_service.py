from abc import ABC, abstractmethod

from src.db.models.student_face import StudentFace


class IStudentFaceService(ABC):

    @abstractmethod
    async def list_faces(self, student_id: int) -> list[StudentFace]:
        pass

    @abstractmethod
    async def add_face(self, student_id: int, image_url: str) -> StudentFace:
        pass

    @abstractmethod
    async def add_face_with_embedding(
        self,
        student_id: int,
        image_url: str,
        embedding: list[float] | None = None,
    ) -> StudentFace:
        pass

    @abstractmethod
    async def delete_face(self, student_id: int, face_id: int) -> None:
        pass
