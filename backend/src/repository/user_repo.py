from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from src.repository.base import BaseRepository
from src.repository.interfaces.i_user_repo import IUserRepository


class UserRepository(BaseRepository, IUserRepository):
    """Concrete implementation của IUserRepository."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Lấy user theo username."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
