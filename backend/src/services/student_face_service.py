import logging

from src.db.models.student_face import StudentFace
from src.repository.interfaces.i_student_face_repo import IStudentFaceRepository
from src.repository.interfaces.i_student_repo import IStudentRepository
from src.services.interfaces.i_student_face_service import IStudentFaceService
from src.utils.exceptions import NotFoundException, ValidationException


class StudentFaceService(IStudentFaceService):
    logger = logging.getLogger(__name__)

    def __init__(self, student_repo: IStudentRepository, face_repo: IStudentFaceRepository):
        self.student_repo = student_repo
        self.face_repo = face_repo

    async def _ensure_student_exists(self, student_id: int):
        student = await self.student_repo.get_by_id(student_id)
        if student is None:
            raise NotFoundException(resource="Sinh viên", identifier=student_id)
        return student

    async def list_faces(self, student_id: int) -> list[StudentFace]:
        await self._ensure_student_exists(student_id)
        return await self.face_repo.get_by_student_id(student_id)

    async def add_face(self, student_id: int, image_url: str) -> StudentFace:
        return await self.add_face_with_embedding(student_id, image_url, None)

    async def add_face_with_embedding(
        self,
        student_id: int,
        image_url: str,
        embedding: list[float] | None = None,
    ) -> StudentFace:
        await self._ensure_student_exists(student_id)
        normalized_url = image_url.strip()
        if not normalized_url:
            raise ValidationException("URL ảnh không hợp lệ", field="image_url")

        safe_embedding = embedding if embedding is not None else []
        face = await self.face_repo.create(
            {
                "student_id": student_id,
                "image_url": normalized_url,
                "embedding": safe_embedding,
            }
        )
        self.logger.info("Added student face id=%s student_id=%s", face.id, student_id)
        return face

    async def delete_face(self, student_id: int, face_id: int) -> None:
        await self._ensure_student_exists(student_id)
        face = await self.face_repo.get_by_id(face_id)
        if face is None or face.student_id != student_id:
            raise NotFoundException(resource="Ảnh khuôn mặt", identifier=face_id)
        await self.face_repo.delete(face_id)
        self.logger.info("Deleted student face id=%s student_id=%s", face_id, student_id)
