from src.dto.common import DataResponse, ListResponse
from src.dto.request.student_face_request import StudentFaceCreateRequest
from src.dto.response.student_face_response import StudentFaceResponse
from src.services.interfaces.i_student_face_service import IStudentFaceService


class StudentFaceController:

    def __init__(self, service: IStudentFaceService):
        self.service = service

    async def get_faces(self, student_id: int) -> ListResponse[StudentFaceResponse]:
        faces = await self.service.list_faces(student_id)
        return ListResponse(
            data=[StudentFaceResponse.model_validate(item) for item in faces],
            total=len(faces),
            page=1,
            page_size=len(faces),
            total_pages=1,
        )

    async def add_face(
        self,
        student_id: int,
        request: StudentFaceCreateRequest,
    ) -> DataResponse[StudentFaceResponse]:
        face = await self.service.add_face_with_embedding(
            student_id=student_id,
            image_url=request.image_url,
            embedding=request.embedding,
        )
        return DataResponse(
            data=StudentFaceResponse.model_validate(face),
            message="Thêm ảnh khuôn mặt thành công",
        )

    async def delete_face(self, student_id: int, face_id: int) -> DataResponse[None]:
        await self.service.delete_face(student_id, face_id)
        return DataResponse(message="Xóa ảnh khuôn mặt thành công")
