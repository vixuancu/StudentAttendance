import math
from typing import Optional

from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.administrative_class_request import (
    AdministrativeClassCreateRequest,
    AdministrativeClassUpdateRequest,
)
from src.dto.response.administrative_class_response import (
    AdministrativeClassItemResponse,
    AdministrativeClassStatsResponse,
)
from src.services.interfaces.i_administrative_class_service import IAdministrativeClassService


class AdministrativeClassController:

    def __init__(self, service: IAdministrativeClassService):
        self.service = service

    @staticmethod
    def _to_response(item) -> AdministrativeClassItemResponse:
        return AdministrativeClassItemResponse(
            id=item.id,
            name=item.name,
            student_count=getattr(item, "student_count", 0),
            is_cancel=item.is_cancel,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def list_classes(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> ListResponse[AdministrativeClassItemResponse]:
        items, total = await self.service.list_classes(
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

    async def get_class(self, class_id: int) -> DataResponse[AdministrativeClassItemResponse]:
        item = await self.service.get_by_id(class_id)
        return DataResponse(
            data=self._to_response(item),
            message="Lấy lớp hành chính thành công",
        )

    async def create_class(
        self,
        request: AdministrativeClassCreateRequest,
    ) -> DataResponse[AdministrativeClassItemResponse]:
        item = await self.service.create(request)
        return DataResponse(
            data=self._to_response(item),
            message="Tạo lớp hành chính thành công",
        )

    async def update_class(
        self,
        class_id: int,
        request: AdministrativeClassUpdateRequest,
    ) -> DataResponse[AdministrativeClassItemResponse]:
        item = await self.service.update(class_id, request)
        return DataResponse(
            data=self._to_response(item),
            message="Cập nhật lớp hành chính thành công",
        )

    async def lock_class(self, class_id: int) -> DataResponse[AdministrativeClassItemResponse]:
        item = await self.service.lock(class_id)
        return DataResponse(
            data=self._to_response(item),
            message="Khóa lớp hành chính thành công",
        )

    async def unlock_class(self, class_id: int) -> DataResponse[AdministrativeClassItemResponse]:
        item = await self.service.unlock(class_id)
        return DataResponse(
            data=self._to_response(item),
            message="Mở khóa lớp hành chính thành công",
        )

    async def hard_delete_class(self, class_id: int) -> DataResponse[None]:
        await self.service.hard_delete(class_id)
        return DataResponse(message="Xóa hẳn lớp hành chính thành công")

    async def get_stats(self, search: Optional[str] = None) -> DataResponse[AdministrativeClassStatsResponse]:
        stats = await self.service.get_stats(search=search)
        return DataResponse(
            data=stats,
            message="Lấy thống kê lớp hành chính thành công",
        )
