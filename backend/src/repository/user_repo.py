from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
