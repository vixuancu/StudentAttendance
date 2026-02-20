from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.user import User


class IUserRepository(ABC):
    """Interface cho UserRepository"""

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Lấy user theo username."""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[User]:
        """Lấy user theo ID."""
        pass
