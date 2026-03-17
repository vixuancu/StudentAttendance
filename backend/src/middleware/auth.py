"""
Auth Dependencies – Xác thực & phân quyền qua FastAPI Depends.
"""

import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.user import User
from src.db.session import get_db
from src.utils.exceptions import ForbiddenException, UnauthorizedException
from src.utils.security import decode_access_token

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException("Token xác thực không được cung cấp")

    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Token không chứa thông tin người dùng")

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException("Token không hợp lệ")

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException("Người dùng không tồn tại")

    if user.is_cancel == 1:
        raise UnauthorizedException("Tài khoản đã bị vô hiệu hóa")

    return user


def require_roles(*allowed_role_names: str):
    """
    Factory dependency: Kiểm tra user có role phù hợp không.
    Sử dụng role_name từ bảng roles (ví dụ: "admin", "giang_vien", "giao_vu").
    """

    async def _role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role_name = current_user.role.role_name if current_user.role else None
        if user_role_name not in allowed_role_names:
            role_names = ", ".join(allowed_role_names)
            logger.warning(
                "Access denied: user=%s role=%s required=%s",
                current_user.username,
                user_role_name,
                role_names,
            )
            raise ForbiddenException(
                f"Chức năng này yêu cầu quyền: {role_names}"
            )
        return current_user

    return _role_checker
