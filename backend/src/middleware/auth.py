"""
Auth Dependencies – Xác thực & phân quyền qua FastAPI Depends.

Sử dụng trong route:
    # Yêu cầu đăng nhập (bất kỳ role)
    @router.get("/profile")
    async def profile(user: User = Depends(get_current_user)):
        ...

    # Yêu cầu role cụ thể
    @router.post("/students")
    async def create_student(
        ...,
        user: User = Depends(require_roles(UserRole.ADMIN, UserRole.GIAO_VU)),
    ):
        ...

Đây là dependency (cách chuẩn FastAPI), KHÔNG phải middleware truyền thống.
Middleware chạy cho MỌI request → lãng phí cho public route.
Dependency chỉ chạy cho route nào khai báo → hiệu quả hơn.
"""

import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.enums import UserRole
from src.db.models.user import User
from src.db.session import get_db
from src.utils.exceptions import ForbiddenException, UnauthorizedException
from src.utils.security import decode_access_token

logger = logging.getLogger(__name__)

# ── HTTPBearer scheme ──
# Tự động extract Bearer token từ header: Authorization: Bearer <token>
# auto_error=False → để ta tự raise exception với message tiếng Việt
_bearer_scheme = HTTPBearer(auto_error=False)


# ===================== GET CURRENT USER ================================= #

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Core auth dependency: JWT → User.

    Flow:
        1. Extract Bearer token từ header
        2. Decode JWT → lấy user_id từ claim "sub"
        3. Query DB → lấy User object mới nhất
        4. Kiểm tra is_active

    Raise:
        UnauthorizedException (401):
            - Không có token
            - Token invalid / expired
            - User không tồn tại
            - User bị vô hiệu hóa
    """
    # 1. Kiểm tra token có được gửi không
    if credentials is None:
        raise UnauthorizedException("Token xác thực không được cung cấp")

    token = credentials.credentials

    # 2. Decode JWT
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn")

    # 3. Lấy user_id từ "sub" claim (chuẩn JWT)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token không chứa thông tin người dùng")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException("Token không hợp lệ")

    # 4. Query user từ DB (luôn lấy mới nhất → bắt được disable account)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException("Người dùng không tồn tại")

    if not user.is_active:
        raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

    return user


# ===================== ROLE-BASED ACCESS ================================ #

def require_roles(*allowed_roles: UserRole):
    """
    Factory dependency: Kiểm tra user có role phù hợp không.

    Sử dụng:
        # Chỉ ADMIN
        Depends(require_roles(UserRole.ADMIN))

        # ADMIN hoặc GIAO_VU
        Depends(require_roles(UserRole.ADMIN, UserRole.GIAO_VU))

        # Tất cả role (= chỉ cần đăng nhập)
        Depends(require_roles(UserRole.ADMIN, UserRole.GIAO_VU, UserRole.GIANG_VIEN))

    Raise:
        ForbiddenException (403): Không đủ quyền
    """

    async def _role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            role_names = ", ".join(r.value for r in allowed_roles)
            logger.warning(
                "Access denied: user=%s role=%s required=%s",
                current_user.username,
                current_user.role.value,
                role_names,
            )
            raise ForbiddenException(
                f"Chức năng này yêu cầu quyền: {role_names}"
            )
        return current_user

    return _role_checker
