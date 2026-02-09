"""
Security utilities – Password hashing & JWT token management.
KHÔNG phụ thuộc vào FastAPI/HTTP.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import settings

logger = logging.getLogger(__name__)

# ===================== PASSWORD HASHING ===================== #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password bằng bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh plain password với hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ===================== JWT TOKEN ===================== #
ALGORITHM = "HS256"


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Tạo JWT access token.

    Payload mẫu:
        {
            "sub": "1",             # user_id (string, chuẩn JWT)
            "username": "admin",
            "role": "ADMIN",
            "exp": 1234567890       # auto-added
        }
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    Giải mã JWT token.
    Trả về payload dict hoặc None nếu token invalid/expired.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed: %s", str(e))
        return None
