from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.controller.account_controller import AccountController
from src.db.models.user import User
from src.deps import get_account_controller
from src.dto.common import DataResponse, ListResponse, PaginationParams
from src.dto.request.account_request import AccountCreateRequest, AccountUpdateRequest
from src.dto.response.account_response import AccountResponse
from src.middleware.auth import require_roles

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=ListResponse[AccountResponse])
async def get_accounts(
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Số bản ghi mỗi trang"),
    search: Optional[str] = Query(None, description="Tìm theo họ tên, username, email"),
    role_name: Optional[str] = Query(None, description="Lọc theo role_name"),
    is_cancel: Optional[bool] = Query(
        None, description="Lọc theo trạng thái khóa tài khoản"
    ),
    _current_user: User = Depends(require_roles("admin")),
    ctrl: AccountController = Depends(get_account_controller),
):
    pagination = PaginationParams(page=page, page_size=page_size)
    return await ctrl.list_accounts(pagination, search, role_name, is_cancel)


@router.get("/{user_id}", response_model=DataResponse[AccountResponse])
async def get_account(
    user_id: int,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: AccountController = Depends(get_account_controller),
):
    return await ctrl.get_account(user_id)


@router.post(
    "",
    response_model=DataResponse[AccountResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    request: AccountCreateRequest,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: AccountController = Depends(get_account_controller),
):
    return await ctrl.create_account(request)


@router.patch("/{user_id}", response_model=DataResponse[AccountResponse])
async def update_account(
    user_id: int,
    request: AccountUpdateRequest,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: AccountController = Depends(get_account_controller),
):
    return await ctrl.update_account(user_id, request)


@router.post("/{user_id}/reset-password", response_model=DataResponse[None])
async def reset_password(
    user_id: int,
    _current_user: User = Depends(require_roles("admin")),
    ctrl: AccountController = Depends(get_account_controller),
):
    return await ctrl.reset_password(user_id)
