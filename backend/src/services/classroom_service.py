import logging
from typing import Optional

from src.db.models.classroom import Classroom
from src.dto.common import PaginationParams
from src.repository.interfaces.i_classroom_repo import IClassroomRepository
from src.repository.interfaces.i_camera_repo import ICameraRepository
from src.services.interfaces.i_classroom_service import IClassroomService
from src.utils.exception import NotFound, AlreadyExists
from src.constant.error_code import ERROR_CODES


class ClassroomService(IClassroomService):
    logger = logging.getLogger(__name__)

    def __init__(
        self,
        classroom_repo: IClassroomRepository,
        camera_repo: ICameraRepository,
    ):
        self.classroom_repo = classroom_repo
        self.camera_repo = camera_repo

    async def get_classrooms(
        self, pagination: PaginationParams, class_name: Optional[str] = None
    ) -> tuple[list[Classroom], int]:
        classrooms, total = await self.classroom_repo.get_classrooms(
            skip=pagination.offset, limit=pagination.limit, class_name=class_name
        )

        return classrooms, total

    async def get_classroom(self, id: int) -> Optional[Classroom]:
        classroom = await self.classroom_repo.get_classroom_by_id(id)

        if not classroom:
            raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)

        return classroom

    async def get_available_classrooms(self) -> list[Classroom]:
        return await self.classroom_repo.get_classrooms_without_camera()

    async def create_classroom(self, request) -> Classroom:
        try:
            data = request.model_dump()

            exist = await self.classroom_repo.get_classroom_by_name(data["class_name"])

            if exist:
                raise AlreadyExists(ERROR_CODES.CLASSROOM.CLASS_NAME_IS_EXISTED)

            classroom = await self.classroom_repo.create_classroom(data)
            return classroom
        except Exception as e:
            raise e

    async def update_classroom(self, id, request) -> Classroom:
        try:
            classroom = await self.classroom_repo.get_classroom_by_id(id)

            if not classroom:
                raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)

            data = request.model_dump(exclude_unset=True)
            new_name = data.get("class_name")

            if new_name and new_name != classroom.class_name:
                existing_class = await self.classroom_repo.get_classroom_by_name(
                    new_name
                )
                if existing_class:
                    raise AlreadyExists(ERROR_CODES.CLASSROOM.CLASS_NAME_IS_EXISTED)

                for key, value in data.items():
                    setattr(classroom, key, value)

            await self.classroom_repo.db.commit()
            await self.classroom_repo.db.refresh(classroom)

            return classroom
        except Exception as e:
            raise e

    async def delete_classroom(self, id: int) -> Classroom:
        try:
            camera_in_class = await self.camera_repo.get_active_camera_by_classroom(id)

            classroom = await self.classroom_repo.delete(id)

            if not classroom:
                raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)

            if camera_in_class:
                await self.camera_repo.delete(camera_in_class.id)

            await self.classroom_repo.db.commit()

            return classroom
        except Exception as e:
            raise e
