import logging
from typing import Optional

from src.db.models.user import User
from src.dto.common import PaginationParams
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest
from src.repository.interfaces.i_user_repo import IUserRepository
from src.services.interfaces.i_account_service import IAccountService
from src.utils.exceptions import AlreadyExistsException, NotFoundException, ValidationException
from src.utils.security import hash_password


class AccountService(IAccountService):
    logger = logging.getLogger(__name__)

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def list_accounts(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
    ) -> tuple[list[User], int]:
        users = await self.user_repo.get_all_users(
            skip=pagination.offset,
            limit=pagination.limit,
            search=search,
            role_name=role_name,
        )
        total = await self.user_repo.count_users(search=search, role_name=role_name)
        return users, total

    async def get_account_by_id(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None or user.is_cancel:
            raise NotFoundException(resource="Tài khoản", identifier=user_id)
        return user

    async def create_account(self, request: AccountCreateRequest) -> User:
        username = request.username.strip()
        email = request.email.strip().lower()

        if not username:
            raise ValidationException("Username không được để trống", field="username")

        existing_by_username = await self.user_repo.get_by_username(username)
        if existing_by_username is not None:
            raise AlreadyExistsException(resource="Tài khoản", field="username", value=username)

        existing_by_email = await self.user_repo.get_by_email(email)
        if existing_by_email is not None:
            raise AlreadyExistsException(resource="Tài khoản", field="email", value=email)

        role = await self.user_repo.get_role_by_id(request.role_id)
        if role is None:
            raise ValidationException("Vai trò không hợp lệ", field="role_id")

        data = {
            "username": username,
            "password": hash_password(request.password),
            "full_name": request.full_name.strip() if request.full_name else None,
            "email": email,
            "gender": request.gender,
            "birth_of_date": request.birth_of_date,
            "role_id": role.id,
            "is_online": False,
            "is_cancel": False,
        }
        user = await self.user_repo.create(data)
        created_user = await self.user_repo.get_by_id(user.id)
        self.logger.info("Created account id=%s username=%s", user.id, username)
        return created_user if created_user is not None else user

    async def update_account(self, user_id: int, request: AccountUpdateRequest) -> User:
        user = await self.get_account_by_id(user_id)
        payload = request.model_dump(exclude_unset=True)

        role_id = payload.pop("role_id", None)
        if role_id is not None:
            role = await self.user_repo.get_role_by_id(role_id)
            if role is None:
                raise ValidationException("Vai trò không hợp lệ", field="role_id")
            payload["role_id"] = role.id

        if "full_name" in payload and payload["full_name"] is not None:
            payload["full_name"] = payload["full_name"].strip()

        updated = await self.user_repo.update(user, payload)
        refreshed = await self.user_repo.get_by_id(updated.id)
        return refreshed if refreshed is not None else updated
