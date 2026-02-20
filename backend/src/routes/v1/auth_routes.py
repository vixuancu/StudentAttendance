"""
Auth Routes – Endpoint xác thực (login, v.v.).
"""

from fastapi import APIRouter, Depends

from src.controller.auth_controller import AuthController
from src.deps import get_auth_controller
from src.dto.common import DataResponse
from src.dto.request.auth_request import LoginRequest
from src.dto.response.auth_response import LoginResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=DataResponse[LoginResponse])
async def login(
    request: LoginRequest,
    ctrl: AuthController = Depends(get_auth_controller),
):
    """Đăng nhập – trả về JWT token và thông tin user"""
    return await ctrl.login(request)
