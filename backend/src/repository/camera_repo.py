from typing import Optional

from sqlalchemy import func, or_, select, update
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
            .order_by(Camera.created_at.desc(), Camera.id.desc())
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

    async def delete(self, id: int) -> Optional[Camera]:
        query = (
            update(Camera)
            .where(Camera.id == id, Camera.is_cancel.is_(False))
            .values(is_cancel=True)
            .returning(Camera)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # async def get_by_camera_name(self, camera_name: str) -> Optional[Camera]:
    #     result = await self.db.execute(
    #         select(Camera)
    #         .where(Camera.camera_name == camera_name)
    #     )
    #     return result.scalar_one_or_none()

    # async def get_by_email(self, email: str) -> Optional[Camera]:
    #     result = await self.db.execute(
    #         select(Camera)
    #         .options(selectinload(Camera.role))
    #         .where(Camera.email == email)
    #     )
    #     return result.scalar_one_or_none()

    # async def get_role_by_name(self, role_name: str) -> Optional[Role]:
    #     result = await self.db.execute(
    #         select(Role).where(Role.role_name == role_name)
    #     )
    #     return result.scalar_one_or_none()

    # async def get_role_by_id(self, role_id: int) -> Optional[Role]:
    #     result = await self.db.execute(select(Role).where(Role.id == role_id))
    #     return result.scalar_one_or_none()

    # async def get_cameras(
    #     self,
    #     skip: int = 0,
    #     limit: int = 10,
    #     search: Optional[str] = None,
    # ) -> list[Camera]:
    #     query = (
    #         select(Camera)
    #         .where(Camera.is_cancel.is_(False))
    #         .order_by(Camera.created_at.desc(), Camera.id.desc())
    #     )

    #     if search:
    #         keyword = f"%{search.strip()}%"
    #         query = query.where(
    #             or_(
    #                 Camera.camera_name.ilike(keyword),
    #                 Camera.ip_address.ilike(keyword),
    #             )
    #         )

    #     query = query.offset(skip).limit(limit)
    #     result = await self.db.execute(query)
    #     return list(result.scalars().all())

    # async def count_cameras(
    #     self,
    #     search: Optional[str] = None,
    # ) -> int:

    #     query = (
    #         select(func.count(Camera.id))
    #         .select_from(Camera)
    #         .where(Camera.is_cancel.is_(False))
    #     )

    #     if search:
    #         keyword = f"%{search.strip()}%"
    #         query = query.where(
    #             or_(
    #                 Camera.camera_name.ilike(keyword),
    #                 Camera.ip_address.ilike(keyword),
    #             )
    #         )

    #     result = await self.db.execute(query)
    #     return result.scalar_one() or 0
