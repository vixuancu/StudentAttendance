from typing import Optional

from sqlalchemy import func, or_, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.role import Role
from src.db.models.camera import Camera
from src.repository.base import BaseRepository
from src.repository.interfaces.i_camera_repo import ICameraRepository


class CameraRepository(BaseRepository, ICameraRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(Camera, db)

    async def get_cameras(
        self,
        skip: int = 0,
        limit: int = 10,
        camera_name: Optional[str] = None,
    ) -> tuple[list[Camera], int]:

        total_count = func.count(Camera.id).over().label("total_count")

        query = (
            select(Camera, total_count)
            .where(Camera.is_cancel.is_(False))
            .order_by(Camera.created_at.desc(), Camera.camera_name.asc())
        )

        if camera_name:
            query = query.where(Camera.camera_name.ilike(f"%{camera_name.strip()}%"))

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        if not rows:
            return [], 0

        cameras = [row[0] for row in rows]
        total = rows[0][1]

        return cameras, total

    async def get_camera_by_name(self, camera_name: str) -> Optional[Camera]:
        result = await self.db.execute(
            select(Camera).where(
                Camera.camera_name == camera_name, Camera.is_cancel.is_(False)
            )
        )
        return result.scalar_one_or_none()

    async def get_camera_by_id(self, id: int) -> Optional[Camera]:
        result = await self.db.execute(
            select(Camera).where(Camera.id == id, Camera.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_camera_by_ip(self, ip: str) -> Optional[Camera]:
        result = await self.db.execute(
            select(Camera).where(Camera.ip_address == ip, Camera.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_active_camera_by_classroom(
        self, classroom_id: int
    ) -> Optional[Camera]:
        result = await self.db.execute(
            select(Camera).where(
                Camera.classroom_id == classroom_id,
                Camera.is_cancel.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> Optional[Camera]:
        query = (
            update(Camera)
            .where(Camera.id == id, Camera.is_cancel.is_(False))
            .values(is_cancel=True, classroom_id=None)
            .returning(Camera)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
