from abc import ABC, abstractmethod
from typing import Optional

from src.db.models.user import User
from src.dto.common import PaginationParams
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest


class IAccountService(ABC):

    @abstractmethod
    async def list_accounts(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> tuple[list[User], int]:
        pass

    @abstractmethod
    async def create_account(self, request: AccountCreateRequest) -> User:
        pass

    @abstractmethod
    async def update_account(self, user_id: int, request: AccountUpdateRequest) -> User:
        pass

    @abstractmethod
    async def get_account_by_id(self, user_id: int) -> User:
        pass
