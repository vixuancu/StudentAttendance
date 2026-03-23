from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.role import Role
from src.db.models.user import User
from src.repository.base import BaseRepository
from src.repository.interfaces.i_user_repo import IUserRepository


class UserRepository(BaseRepository, IUserRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.role_name == role_name)
        )
        return result.scalar_one_or_none()

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_all_roles(self) -> list[Role]:
        result = await self.db.execute(
            select(Role)
            .where(Role.is_cancel.is_(False))
            .order_by(Role.id.asc())
        )
        return list(result.scalars().all())

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> list[User]:
        query = (
            select(User)
            .options(selectinload(User.role))
            .join(Role, User.role_id == Role.id)
            .where(Role.is_cancel.is_(False))
            .order_by(User.created_at.desc(), User.id.desc())
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(
                or_(
                    User.full_name.ilike(keyword),
                    User.email.ilike(keyword),
                    User.username.ilike(keyword),
                )
            )

        if role_name:
            query = query.where(Role.role_name == role_name)

        if is_cancel is not None:
            query = query.where(User.is_cancel.is_(is_cancel))

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_users(
        self,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> int:
        query = (
            select(func.count(User.id))
            .select_from(User)
            .join(Role, User.role_id == Role.id)
            .where(Role.is_cancel.is_(False))
        )

        if search:
            keyword = f"%{search.strip()}%"
            query = query.where(
                or_(
                    User.full_name.ilike(keyword),
                    User.email.ilike(keyword),
                    User.username.ilike(keyword),
                )
            )

        if role_name:
            query = query.where(Role.role_name == role_name)

        if is_cancel is not None:
            query = query.where(User.is_cancel.is_(is_cancel))

        result = await self.db.execute(query)
        return result.scalar_one() or 0
