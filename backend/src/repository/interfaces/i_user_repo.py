from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.role import Role
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

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Lấy user theo email."""
        pass

    @abstractmethod
    async def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Lấy role theo role_name."""
        pass

    @abstractmethod
    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Lấy role theo id."""
        pass

    @abstractmethod
    async def get_all_roles(self) -> list[Role]:
        """Lấy danh sách role còn hiệu lực."""
        pass

    @abstractmethod
    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> list[User]:
        """Lấy danh sách users có filter."""
        pass

    @abstractmethod
    async def count_users(
        self,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> int:
        """Đếm users có filter."""
        pass

    @abstractmethod
    async def update(self, db_obj: User, data: dict) -> User:
        """Cập nhật thông tin user."""
        pass

    @abstractmethod
    async def create(self, data: dict) -> User:
        """Tạo user mới."""
        pass
