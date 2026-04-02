import math
from typing import Optional

from src.db.models.course import Course
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.course_request import CourseCreateRequest, CourseUpdateRequest
from src.dto.response.course_response import CourseResponse
from src.services.interfaces.i_course_service import ICourseService


class CourseController:

    def __init__(self, service: ICourseService):
        self.service = service

    @staticmethod
    def _to_response(item: Course) -> CourseResponse:
        return CourseResponse(
            id=item.id,
            course_name=item.course_name,
            is_cancel=item.is_cancel,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def list_courses(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> ListResponse[CourseResponse]:
        items, total = await self.service.list_courses(
            pagination=pagination,
            search=search,
            is_cancel=is_cancel,
        )
        return ListResponse(
            data=[self._to_response(item) for item in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def get_by_id(self, course_id: int) -> DataResponse[CourseResponse]:
        item = await self.service.get_by_id(course_id)
        return DataResponse(data=self._to_response(item), message="Lấy khóa học thành công")

    async def create(self, request: CourseCreateRequest) -> DataResponse[CourseResponse]:
        item = await self.service.create(request)
        return DataResponse(data=self._to_response(item), message="Tạo khóa học thành công")

    async def update(self, course_id: int, request: CourseUpdateRequest) -> DataResponse[CourseResponse]:
        item = await self.service.update(course_id, request)
        return DataResponse(data=self._to_response(item), message="Cập nhật khóa học thành công")

    async def delete(self, course_id: int) -> DataResponse[None]:
        await self.service.delete(course_id)
        return DataResponse(message="Xóa khóa học thành công")