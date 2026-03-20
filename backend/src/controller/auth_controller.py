"""
AuthController – Điều phối xác thực.
Nhận request → gọi Service → map Response DTO.
"""

from src.dto.common import DataResponse
from src.dto.request.auth_request import ChangePasswordRequest, LoginRequest
from src.dto.response.auth_response import LoginResponse, TokenResponse, UserInfoResponse
from src.services.interfaces.i_auth_service import IAuthService


class AuthController:
    def __init__(self, service: IAuthService):
        self.service = service

    async def login(self, request: LoginRequest) -> DataResponse[LoginResponse]:
        user, access_token = await self.service.login(request)

        # Lấy role_name từ relationship nếu có
        role_name = user.role.role_name if user.role else None

        login_data = LoginResponse(
            token=TokenResponse(access_token=access_token),
            user=UserInfoResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                role_id=user.role_id,
                role_name=role_name,
            ),
        )

        return DataResponse(
            data=login_data,
            message="Đăng nhập thành công",
        )

    async def me(self, user_id: int) -> DataResponse[UserInfoResponse]:
        user = await self.service.get_current_user(user_id)

        role_name = user.role.role_name if user.role else None
        user_data = UserInfoResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            role_id=user.role_id,
            role_name=role_name,
        )

        return DataResponse(
            data=user_data,
            message="Lấy thông tin tài khoản thành công",
        )

    async def change_password(
        self, user_id: int, request: ChangePasswordRequest
    ) -> DataResponse[None]:
        await self.service.change_password(user_id, request)
        return DataResponse(message="Đổi mật khẩu thành công")
