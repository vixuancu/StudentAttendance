"""
AuthController – Điều phối xác thực.
Nhận request → gọi Service → map Response DTO.
"""

from src.dto.common import DataResponse
from src.dto.request.auth_request import LoginRequest
from src.dto.response.auth_response import LoginResponse, TokenResponse, UserInfoResponse
from src.services.interfaces.i_auth_service import IAuthService


class AuthController:
    """Controller điều phối cho Auth – nhận IAuthService qua DI."""

    def __init__(self, service: IAuthService):
        self.service = service

    async def login(self, request: LoginRequest) -> DataResponse[LoginResponse]:
        user, access_token = await self.service.login(request)

        login_data = LoginResponse(
            token=TokenResponse(access_token=access_token),
            user=UserInfoResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role.value,
            ),
        )

        return DataResponse(
            data=login_data,
            message="Đăng nhập thành công",
        )
