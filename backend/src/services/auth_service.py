"""
AuthService – Business logic xác thực người dùng.
KHÔNG import FastAPI/HTTP. Chỉ throw BusinessException.
"""

import logging

from src.db.models.user import User
from src.dto.request.auth_request import LoginRequest
from src.repository.interfaces.i_user_repo import IUserRepository
from src.services.interfaces.i_auth_service import IAuthService
from src.utils.exceptions import UnauthorizedException
from src.utils.security import create_access_token, verify_password


class AuthService(IAuthService):
    logger = logging.getLogger(__name__)

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def login(self, request: LoginRequest) -> tuple[User, str]:
        """
        Xác thực user → tạo JWT token.

        Flow:
            1. Tìm user theo username
            2. Kiểm tra password
            3. Kiểm tra is_active
            4. Tạo JWT access token

        Raise:
            UnauthorizedException: Sai credentials hoặc tài khoản bị khóa
        """
        # 1. Tìm user
        user = await self.user_repo.get_by_username(request.username)
        if user is None:
            self.logger.warning("Login failed: user '%s' not found", request.username)
            raise UnauthorizedException("Tên đăng nhập hoặc mật khẩu không đúng")

        # 2. Kiểm tra password
        if not verify_password(request.password, user.password_hash):
            self.logger.warning("Login failed: wrong password for user '%s'", request.username)
            raise UnauthorizedException("Tên đăng nhập hoặc mật khẩu không đúng")

        # 3. Kiểm tra active
        if not user.is_active:
            self.logger.warning("Login failed: user '%s' is disabled", request.username)
            raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

        # 4. Tạo JWT token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
        }
        access_token = create_access_token(data=token_data)

        self.logger.info("User '%s' logged in successfully", request.username)
        return user, access_token
