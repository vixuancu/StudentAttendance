"""
AuthService – Business logic xác thực người dùng.
KHÔNG import FastAPI/HTTP. Chỉ throw BusinessException.
"""

import logging
import random

from src.db.models.user import User
from src.config.settings import settings
from src.dto.request.auth_request import (
    ChangePasswordRequest,
    ForgotPasswordConfirmRequest,
    ForgotPasswordRequest,
    LoginRequest,
)
from src.repository.interfaces.i_user_repo import IUserRepository
from src.services.interfaces.i_auth_service import ForgotPasswordDispatch, IAuthService
from src.services.otp_cache import otp_memory_cache
from src.utils.exceptions import UnauthorizedException, ValidationException
from src.utils.security import create_access_token, hash_password, verify_password


class AuthService(IAuthService):
    logger = logging.getLogger(__name__)

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def login(self, request: LoginRequest) -> tuple[User, str]:
        # 1. Tìm user
        user = await self.user_repo.get_by_username(request.username)
        if user is None:
            self.logger.warning("Login failed: user '%s' not found", request.username)
            raise UnauthorizedException("Tên đăng nhập hoặc mật khẩu không đúng")

        # 2. Kiểm tra password (field đổi từ password_hash → password)
        if not verify_password(request.password, user.password):
            self.logger.warning("Login failed: wrong password for user '%s'", request.username)
            raise UnauthorizedException("Tên đăng nhập hoặc mật khẩu không đúng")

        # 3. Kiểm tra is_cancel (thay cho is_active)
        if user.is_cancel:
            self.logger.warning("Login failed: user '%s' is cancelled", request.username)
            raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

        # 4. Tạo JWT token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role_id": user.role_id,
        }
        access_token = create_access_token(data=token_data)

        self.logger.info("User '%s' logged in successfully", request.username)
        return user, access_token

    async def get_current_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UnauthorizedException("Người dùng không tồn tại")

        if user.is_cancel:
            raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

        return user

    async def change_password(
        self, user_id: int, request: ChangePasswordRequest
    ) -> None:
        user = await self.get_current_user(user_id)

        if not verify_password(request.old_password, user.password):
            raise ValidationException("Mật khẩu hiện tại không đúng", field="old_password")

        if request.old_password == request.new_password:
            raise ValidationException(
                "Mật khẩu mới phải khác mật khẩu hiện tại", field="new_password"
            )

        new_hashed_password = hash_password(request.new_password)
        await self.user_repo.update(user, {"password": new_hashed_password})
        self.logger.info("User '%s' changed password successfully", user.username)

    async def request_forgot_password(
        self,
        request: ForgotPasswordRequest,
    ) -> ForgotPasswordDispatch:
        email = request.email.strip().lower()
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise ValidationException("Email không tồn tại trong hệ thống", field="email")

        otp = f"{random.randint(0, 999999):06d}"
        otp_memory_cache.set(
            email=email,
            otp=otp,
            ttl_seconds=settings.forgot_password_otp_ttl_seconds,
        )

        self.logger.info("Created forgot-password OTP for email=%s", email)
        return ForgotPasswordDispatch(email=email, otp=otp)

    async def confirm_forgot_password(
        self,
        request: ForgotPasswordConfirmRequest,
    ) -> None:
        email = request.email.strip().lower()
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise ValidationException("Email không tồn tại trong hệ thống", field="email")

        is_valid_otp = otp_memory_cache.verify(email=email, otp=request.otp)
        if not is_valid_otp:
            raise ValidationException(
                "Mã xác thực không đúng hoặc mật khẩu mới không hợp lệ",
                field="otp",
            )

        await self.user_repo.update(user, {"password": hash_password(request.new_password)})
        self.logger.info("Forgot-password confirm success for email=%s", email)
