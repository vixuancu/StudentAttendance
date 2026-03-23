from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.db.models.user import User
from src.dto.request.auth_request import (
    ChangePasswordRequest,
    ForgotPasswordConfirmRequest,
    ForgotPasswordRequest,
    LoginRequest,
)


@dataclass
class ForgotPasswordDispatch:
    email: str
    otp: str


class IAuthService(ABC):
    """Interface cho AuthService – xử lý xác thực."""

    @abstractmethod
    async def login(self, request: LoginRequest) -> tuple[User, str]:
        """
        Xác thực user và trả về (User, access_token).
        Raise UnauthorizedException nếu sai credentials.
        """
        pass

    @abstractmethod
    async def get_current_user(self, user_id: int) -> User:
        """Lấy thông tin user hiện tại theo user_id từ token."""
        pass

    @abstractmethod
    async def change_password(
        self, user_id: int, request: ChangePasswordRequest
    ) -> None:
        """Đổi mật khẩu user hiện tại."""
        pass

    @abstractmethod
    async def request_forgot_password(
        self,
        request: ForgotPasswordRequest,
    ) -> ForgotPasswordDispatch:
        """Kiểm tra email tồn tại, tạo OTP và trả payload để gửi mail nền."""
        pass

    @abstractmethod
    async def confirm_forgot_password(
        self,
        request: ForgotPasswordConfirmRequest,
    ) -> None:
        """Xác thực OTP và cập nhật mật khẩu mới."""
        pass
