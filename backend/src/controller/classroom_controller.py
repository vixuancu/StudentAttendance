import math
from typing import Optional

from src.dto.common import DataResponse, PaginationParams, ListResponse
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest
from src.dto.request.classroom_request import (
    ClassroomCreateRequest,
    ClassroomUpdateRequest,
)
from src.dto.response.classroom_response import ClassroomResponse
from src.services.interfaces.i_classroom_service import IClassroomService


class ClassroomController:

    def __init__(self, service: IClassroomService):
        self.service = service

    async def get_classrooms(
        self, pagination: PaginationParams, class_name: Optional[str] = None
    ) -> ListResponse[ClassroomResponse]:
        classrooms, total = await self.service.get_classrooms(
            pagination=pagination, class_name=class_name
        )

        return ListResponse(
            data=[
                ClassroomResponse.model_validate(classroom) for classroom in classrooms
            ],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def get_classroom(self, id: int) -> DataResponse[ClassroomResponse]:
        classroom = await self.service.get_classroom(id)

        return DataResponse(
            data=ClassroomResponse.model_validate(classroom),
            message="Lấy thông tin phòng học thành công",
        )

    async def create_classroom(
        self, request: ClassroomCreateRequest
    ) -> DataResponse[ClassroomResponse]:
        classroom = await self.service.create_classroom(request)

        return DataResponse(
            data=ClassroomResponse.model_validate(classroom),
            message="Thêm phòng học thành công",
        )

    async def update_classroom(
        self, id: int, request: ClassroomUpdateRequest
    ) -> DataResponse[ClassroomResponse]:
        classroom = await self.service.update_classroom(id, request)

        return DataResponse(
            data=ClassroomResponse.model_validate(classroom),
            message="Cập nhật phòng học thành công",
        )

    async def delete_classroom(self, id: int) -> DataResponse[ClassroomResponse]:
        classroom = await self.service.delete_classroom(id)

        return DataResponse(
            data=ClassroomResponse.model_validate(classroom),
            message="Xóa phòng học thành công",
        )

    async def get_available_classrooms(self) -> DataResponse[ClassroomResponse]:
        classrooms = await self.service.get_available_classrooms()

        return DataResponse(
            data=[
                ClassroomResponse(
                    id=classroom.id,
                    class_name=classroom.class_name,
                    created_at=classroom.created_at,
                    updated_at=classroom.updated_at,
                    camera=None,
                )
                for classroom in classrooms
            ],
        )
