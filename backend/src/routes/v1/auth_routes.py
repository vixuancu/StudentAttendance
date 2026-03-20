"""
Auth Routes – Endpoint xác thực (login, v.v.).
"""

from fastapi import APIRouter, Depends

from src.controller.auth_controller import AuthController
from src.db.models.user import User
from src.deps import get_auth_controller
from src.dto.common import DataResponse
from src.dto.request.auth_request import ChangePasswordRequest, LoginRequest
from src.dto.response.auth_response import LoginResponse, UserInfoResponse
from src.middleware.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=DataResponse[LoginResponse])
async def login(
    request: LoginRequest,
    ctrl: AuthController = Depends(get_auth_controller),
):
    """Đăng nhập – trả về JWT token và thông tin user"""
    return await ctrl.login(request)


@router.get("/me", response_model=DataResponse[UserInfoResponse])
async def me(
    current_user: User = Depends(get_current_user),
    ctrl: AuthController = Depends(get_auth_controller),
):
    """Lấy thông tin user hiện tại từ access token"""
    return await ctrl.me(current_user.id)


@router.post("/change-password", response_model=DataResponse[None])
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    ctrl: AuthController = Depends(get_auth_controller),
):
    """Đổi mật khẩu cho user hiện tại"""
    return await ctrl.change_password(current_user.id, request)
