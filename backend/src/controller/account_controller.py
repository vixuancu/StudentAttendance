import math
from typing import Optional

from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest
from src.dto.response.account_response import AccountResponse, RoleOptionResponse
from src.services.interfaces.i_account_service import IAccountService


class AccountController:

    def __init__(self, service: IAccountService):
        self.service = service

    @staticmethod
    def _to_response_model(user) -> AccountResponse:
        role = user.__dict__.get("role")
        return AccountResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            gender=user.gender,
            birth_of_date=user.birth_of_date,
            role_id=user.role_id,
            role_name=role.role_name if role else None,
            is_cancel=user.is_cancel,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def list_accounts(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        role_name: Optional[str] = None,
        is_cancel: Optional[bool] = None,
    ) -> ListResponse[AccountResponse]:
        users, total = await self.service.list_accounts(
            pagination=pagination,
            search=search,
            role_name=role_name,
            is_cancel=is_cancel,
        )

        return ListResponse(
            data=[self._to_response_model(user) for user in users],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=math.ceil(total / pagination.page_size) if total else 0,
        )

    async def create_account(
        self,
        request: AccountCreateRequest,
    ) -> DataResponse[AccountResponse]:
        user = await self.service.create_account(request)
        return DataResponse(
            data=self._to_response_model(user),
            message="Tạo tài khoản thành công",
        )

    async def update_account(
        self,
        user_id: int,
        request: AccountUpdateRequest,
    ) -> DataResponse[AccountResponse]:
        user = await self.service.update_account(user_id, request)
        return DataResponse(
            data=self._to_response_model(user),
            message="Cập nhật tài khoản thành công",
        )

    async def get_account(self, user_id: int) -> DataResponse[AccountResponse]:
        user = await self.service.get_account_by_id(user_id)
        return DataResponse(
            data=self._to_response_model(user),
            message="Lấy thông tin tài khoản thành công",
        )

    async def reset_password(self, user_id: int) -> DataResponse[None]:
        await self.service.reset_password(user_id)
        return DataResponse(message="Đặt lại mật khẩu thành công")

    async def list_roles(self) -> ListResponse[RoleOptionResponse]:
        roles = await self.service.list_roles()
        return ListResponse(
            data=[RoleOptionResponse(id=role.id, role_name=role.role_name) for role in roles],
            total=len(roles),
            page=1,
            page_size=len(roles),
            total_pages=1,
        )
