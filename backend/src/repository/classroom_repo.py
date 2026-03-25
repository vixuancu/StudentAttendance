from typing import Optional

from sqlalchemy import and_, func, or_, select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.db.models.classroom import Classroom
from src.db.models.camera import Camera
from src.repository.base import BaseRepository
from src.repository.interfaces.i_classroom_repo import IClassroomRepository


class ClassroomRepository(BaseRepository, IClassroomRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(Classroom, db)

    async def get_classrooms(
        self,
        skip: int = 0,
        limit: int = 10,
        class_name: Optional[str] = None,
    ) -> tuple[list[Classroom], int]:

        total_count = func.count(Classroom.id).over().label("total_count")

        query = (
            select(Classroom, total_count)
            .options(joinedload(Classroom.camera))
            .where(Classroom.is_cancel.is_(False))
            .order_by(Classroom.created_at.desc(), Classroom.id.desc())
        )

        if class_name:
            query = query.where(Classroom.class_name.ilike(f"%{class_name.strip()}%"))

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        if not rows:
            return [], 0

        classrooms = [row[0] for row in rows]
        total = rows[0][1]

        return classrooms, total

    async def get_classroom_by_id(self, id: int) -> Optional[Classroom]:
        result = await self.db.execute(
            select(Classroom)
            .options(joinedload(Classroom.camera))
            .where(Classroom.id == id, Classroom.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_classroom_by_name(self, class_name: str) -> Optional[Classroom]:
        result = await self.db.execute(
            select(Classroom)
            .options(joinedload(Classroom.camera))
            .where(Classroom.class_name == class_name, Classroom.is_cancel.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_classrooms_without_camera(self) -> list[Classroom]:
        query = (
            select(Classroom)
            .outerjoin(
                Camera,
                and_(
                    Classroom.id == Camera.classroom_id,
                    Camera.is_cancel.is_(False),
                ),
            )
            .where(Classroom.is_cancel.is_(False), Camera.id.is_(None))
            .options(selectinload(Classroom.camera))
            .order_by(Classroom.class_name.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_classroom(self, data):
        stmt = insert(Classroom).values(**data).returning(Classroom)
        result = await self.db.execute(stmt)
        new_obj = result.scalar_one()

        query = (
            select(Classroom)
            .options(joinedload(Classroom.camera))
            .where(Classroom.id == new_obj.id)
        )
        final_res = await self.db.execute(query)
        return final_res.scalar_one()

    async def delete(self, id: int) -> Optional[Classroom]:
        query = (
            update(Classroom)
            .where(Classroom.id == id, Classroom.is_cancel.is_(False))
            .values(is_cancel=True)
            .returning(Classroom)
        )
        result = await self.db.execute(query)
        classroom = result.scalar_one_or_none()

        if not classroom:
            return None

        refresh_query = (
            select(Classroom)
            .options(joinedload(Classroom.camera))
            .where(Classroom.id == classroom.id)
        )
        refresh_result = await self.db.execute(refresh_query)
        return refresh_result.scalar_one()
