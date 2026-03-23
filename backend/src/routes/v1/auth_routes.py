"""
Auth Routes – Endpoint xác thực (login, v.v.).
"""

from fastapi import APIRouter, BackgroundTasks, Depends

from src.controller.auth_controller import AuthController
from src.db.models.user import User
from src.deps import get_auth_controller, get_mail_provider
from src.dto.common import DataResponse
from src.dto.request.auth_request import (
    ChangePasswordRequest,
    ForgotPasswordConfirmRequest,
    ForgotPasswordRequest,
    LoginRequest,
)
from src.dto.response.auth_response import LoginResponse, UserInfoResponse
from src.middleware.auth import get_current_user
from src.services.interfaces.i_mail_provider import IMailProvider

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


@router.post("/forgot-password/request", response_model=DataResponse[None])
async def request_forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    ctrl: AuthController = Depends(get_auth_controller),
    mail_provider: IMailProvider = Depends(get_mail_provider),
):
    """Kiểm tra email tồn tại và gửi OTP nền qua email."""
    dispatch = await ctrl.request_forgot_password(request)
    background_tasks.add_task(
        mail_provider.send_forgot_password_otp,
        dispatch.email,
        dispatch.otp,
    )
    return DataResponse(message="Mã xác thực đang được gửi tới email")


@router.post("/forgot-password/confirm", response_model=DataResponse[None])
async def confirm_forgot_password(
    request: ForgotPasswordConfirmRequest,
    ctrl: AuthController = Depends(get_auth_controller),
):
    """Xác thực OTP và đặt mật khẩu mới."""
    return await ctrl.confirm_forgot_password(request)
