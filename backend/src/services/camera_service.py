import time
import logging
import asyncio
from typing import Optional
from sqlalchemy.exc import IntegrityError

from src.db.models.camera import Camera
from src.dto.common import PaginationParams
from src.repository.interfaces.i_camera_repo import ICameraRepository
from src.repository.interfaces.i_classroom_repo import IClassroomRepository
from src.services.interfaces.i_camera_service import ICameraService
from src.utils.exception import NotFound, AlreadyExists
from src.constant.error_code import ERROR_CODES


class CameraService(ICameraService):
    logger = logging.getLogger(__name__)

    def __init__(
        self, camera_repo: ICameraRepository, classroom_repo: IClassroomRepository
    ):
        self.camera_repo = camera_repo
        self.classroom_repo = classroom_repo

    async def get_cameras(
        self, pagination: PaginationParams, camera_name: Optional[str] = None
    ) -> tuple[list[Camera], int]:
        cameras, total = await self.camera_repo.get_cameras(
            skip=pagination.offset, limit=pagination.limit, camera_name=camera_name
        )

        return cameras, total

    async def get_camera(self, id: int) -> Optional[Camera]:
        camera = await self.camera_repo.get_camera_by_id(id)

        if not camera:
            raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

        return camera

    def _map_integrity_error(self, error: IntegrityError) -> None:
        detail = str(getattr(error, "orig", error)).lower()

        if "cameras_ip_address_key" in detail or "ip_address" in detail:
            raise AlreadyExists(ERROR_CODES.CAMERA.IP_ADDRESS_IS_EXISTED)

        if "cameras_classroom_id_key" in detail or "classroom_id" in detail:
            raise AlreadyExists(ERROR_CODES.CAMERA.CLASSROOM_ALREADY_HAS_CAMERA)

        raise error

    async def create_camera(self, request) -> Camera:
        data = request.model_dump()

        results = await asyncio.gather(
            self.camera_repo.get_camera_by_name(data["camera_name"]),
            self.camera_repo.get_camera_by_ip(data["ip_address"]),
            self.classroom_repo.get_classroom_by_id(data["classroom_id"]),
            self.camera_repo.get_active_camera_by_classroom(data["classroom_id"]),
        )

        existing_name, existing_ip, classroom, camera_in_room = results

        if existing_name:
            raise AlreadyExists(ERROR_CODES.CAMERA.CAMERA_NAME_IS_EXISTED)
        if existing_ip:
            raise AlreadyExists(ERROR_CODES.CAMERA.IP_ADDRESS_IS_EXISTED)
        if not classroom:
            raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)
        if camera_in_room:
            raise AlreadyExists(ERROR_CODES.CAMERA.CLASSROOM_ALREADY_HAS_CAMERA)

        try:
            camera = await self.camera_repo.create(data)
            return camera
        except IntegrityError as exc:
            await self.camera_repo.db.rollback()
            self._map_integrity_error(exc)

        # async def update_camera(self, id: int, request) -> Camera:
        camera = await self.camera_repo.get_camera_by_id(id)
        if not camera:
            raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

        data = request.model_dump(exclude_unset=True)

        new_name = data.get("camera_name")
        new_ip = data.get("ip_address")
        new_room_id = data.get("classroom_id")

        checks = []
        if new_name and new_name != camera.camera_name:
            checks.append(self.camera_repo.get_camera_by_name(new_name))
        else:
            checks.append(asyncio.sleep(0, result=None))

        if new_ip and new_ip != camera.ip_address:
            checks.append(self.camera_repo.get_camera_by_ip(new_ip))
        else:
            checks.append(asyncio.sleep(0, result=None))

        if new_room_id and new_room_id != camera.classroom_id:
            checks.append(self.classroom_repo.get_classroom_by_id(new_room_id))
            checks.append(self.camera_repo.get_active_camera_by_classroom(new_room_id))
        else:
            checks.append(asyncio.sleep(0, result=None))
            checks.append(asyncio.sleep(0, result=None))

        results = await asyncio.gather(*checks)
        existing_name, existing_ip, classroom, camera_in_room = results

        if existing_name:
            raise AlreadyExists(ERROR_CODES.CAMERA.CAMERA_NAME_IS_EXISTED)
        if existing_ip:
            raise AlreadyExists(ERROR_CODES.CAMERA.IP_ADDRESS_IS_EXISTED)
        if new_room_id and new_room_id != camera.classroom_id:
            if not classroom:
                raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)
            if camera_in_room:
                raise AlreadyExists(ERROR_CODES.CAMERA.CLASSROOM_ALREADY_HAS_CAMERA)

        for key, value in data.items():
            setattr(camera, key, value)

        await self.camera_repo.db.commit()
        await self.camera_repo.db.refresh(camera)

        return camera

    async def update_camera(self, id: int, request) -> Camera:
        start_total = time.perf_counter()

        t0 = time.perf_counter()
        camera = await self.camera_repo.get_camera_by_id(id)
        t_get_camera_ms = (time.perf_counter() - t0) * 1000
        if not camera:
            raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

        data = request.model_dump(exclude_unset=True)

        new_name = data.get("camera_name")
        new_ip = data.get("ip_address")
        new_room_id = data.get("classroom_id")

        checks = []

        if new_name and new_name != camera.camera_name:
            checks.append(self.camera_repo.get_camera_by_name(new_name))
        else:
            checks.append(asyncio.sleep(0, result=None))

        if new_ip and new_ip != camera.ip_address:
            checks.append(self.camera_repo.get_camera_by_ip(new_ip))
        else:
            checks.append(asyncio.sleep(0, result=None))

        if new_room_id and new_room_id != camera.classroom_id:
            checks.append(self.classroom_repo.get_classroom_by_id(new_room_id))
            checks.append(self.camera_repo.get_active_camera_by_classroom(new_room_id))
        else:
            checks.append(asyncio.sleep(0, result=None))
            checks.append(asyncio.sleep(0, result=None))

        t0 = time.perf_counter()
        results = await asyncio.gather(*checks)
        t_checks_ms = (time.perf_counter() - t0) * 1000

        existing_name, existing_ip, classroom, camera_in_room = results

        if existing_name:
            raise AlreadyExists(ERROR_CODES.CAMERA.CAMERA_NAME_IS_EXISTED)
        if existing_ip:
            raise AlreadyExists(ERROR_CODES.CAMERA.IP_ADDRESS_IS_EXISTED)

        if new_room_id and new_room_id != camera.classroom_id:
            if not classroom:
                raise NotFound(ERROR_CODES.CLASSROOM.CLASSROOM_NOT_FOUND)
            if camera_in_room:
                raise AlreadyExists(ERROR_CODES.CAMERA.CLASSROOM_ALREADY_HAS_CAMERA)

        for key, value in data.items():
            setattr(camera, key, value)

        t0 = time.perf_counter()
        try:
            await self.camera_repo.db.commit()
        except IntegrityError as exc:
            await self.camera_repo.db.rollback()
            self._map_integrity_error(exc)
        t_commit_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        await self.camera_repo.db.refresh(camera)
        t_refresh_ms = (time.perf_counter() - t0) * 1000

        t_total_ms = (time.perf_counter() - start_total) * 1000
        self.logger.info(
            "camera.update id=%s timings: get_camera=%.2fms checks=%.2fms commit=%.2fms refresh=%.2fms total=%.2fms",
            id,
            t_get_camera_ms,
            t_checks_ms,
            t_commit_ms,
            t_refresh_ms,
            t_total_ms,
        )

        return camera

    async def delete_camera(self, id: int) -> Camera:
        camera = await self.camera_repo.delete(id)

        if not camera:
            raise NotFound(ERROR_CODES.CAMERA.CAMERA_NOT_FOUND)

        return camera
