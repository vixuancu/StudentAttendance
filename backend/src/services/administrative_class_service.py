import logging
from typing import Optional

from src.db.models.administrative_class import AdministrativeClass
from src.dto.common import PaginationParams
from src.dto.request.administrative_class_request import (
    AdministrativeClassCreateRequest,
    AdministrativeClassUpdateRequest,
)
from src.dto.response.administrative_class_response import AdministrativeClassStatsResponse
from src.repository.interfaces.i_administrative_class_repo import IAdministrativeClassRepository
from src.services.interfaces.i_administrative_class_service import IAdministrativeClassService
from src.utils.exceptions import AlreadyExistsException, NotFoundException, ValidationException


class AdministrativeClassService(IAdministrativeClassService):
    logger = logging.getLogger(__name__)

    def __init__(self, repo: IAdministrativeClassRepository):
        self.repo = repo

    async def list_classes(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ):
        items = await self.repo.list_classes(
            skip=pagination.offset,
            limit=pagination.limit,
            search=search,
            is_cancel=is_cancel,
        )
        total = await self.repo.count_classes(search=search, is_cancel=is_cancel)
        count_map = await self.repo.count_students_by_class_ids([item.id for item in items])
        for item in items:
            setattr(item, "student_count", count_map.get(item.id, 0))
        return items, total

    async def get_by_id(self, class_id: int):
        item = await self.repo.get_by_id(class_id)
        if item is None:
            raise NotFoundException(resource="Lớp hành chính", identifier=class_id)
        count = await self.repo.count_students_by_class_id(item.id)
        setattr(item, "student_count", count)
        return item

    async def create(self, request: AdministrativeClassCreateRequest):
        name = request.name.strip()
        if not name:
            raise ValidationException("Tên lớp hành chính không được để trống", field="name")

        existed = await self.repo.get_by_name_ci(name)
        if existed is not None:
            raise AlreadyExistsException(resource="Lớp hành chính", field="name", value=name)

        created = await self.repo.create({"name": name, "is_cancel": False})
        setattr(created, "student_count", 0)
        return created

    async def update(self, class_id: int, request: AdministrativeClassUpdateRequest):
        item = await self.get_by_id(class_id)
        name = request.name.strip()
        if not name:
            raise ValidationException("Tên lớp hành chính không được để trống", field="name")

        existed = await self.repo.get_by_name_ci(name)
        if existed is not None and existed.id != item.id:
            raise AlreadyExistsException(resource="Lớp hành chính", field="name", value=name)

        updated = await self.repo.update(item, {"name": name})
        count = await self.repo.count_students_by_class_id(updated.id)
        setattr(updated, "student_count", count)
        return updated

    async def lock(self, class_id: int):
        item = await self.get_by_id(class_id)
        if item.is_cancel:
            count = await self.repo.count_students_by_class_id(item.id)
            setattr(item, "student_count", count)
            return item
        updated = await self.repo.update(item, {"is_cancel": True})
        count = await self.repo.count_students_by_class_id(updated.id)
        setattr(updated, "student_count", count)
        return updated

    async def unlock(self, class_id: int):
        item = await self.get_by_id(class_id)
        if not item.is_cancel:
            count = await self.repo.count_students_by_class_id(item.id)
            setattr(item, "student_count", count)
            return item
        updated = await self.repo.update(item, {"is_cancel": False})
        count = await self.repo.count_students_by_class_id(updated.id)
        setattr(updated, "student_count", count)
        return updated

    async def get_stats(self, search: Optional[str] = None) -> AdministrativeClassStatsResponse:
        total = await self.repo.count_classes(search=search, is_cancel=None)
        active_count = await self.repo.count_classes(search=search, is_cancel=False)
        locked_count = await self.repo.count_classes(search=search, is_cancel=True)
        return AdministrativeClassStatsResponse(
            total=total,
            active_count=active_count,
            locked_count=locked_count,
        )
