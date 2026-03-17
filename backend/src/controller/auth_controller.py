"""
AuthController – Điều phối xác thực.
Nhận request → gọi Service → map Response DTO.
"""

from src.dto.common import DataResponse
from src.dto.request.auth_request import LoginRequest
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
