from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AccountCreateRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Tên đăng nhập")
    email: str = Field(..., min_length=3, max_length=255, description="Email")
    password: str = Field(..., min_length=6, max_length=128, description="Mật khẩu")
    full_name: Optional[str] = Field(None, max_length=100, description="Họ và tên")
    gender: Optional[bool] = Field(None, description="Giới tính: false=Nữ, true=Nam")
    birth_of_date: Optional[datetime] = Field(None, description="Ngày sinh")
    role_id: int = Field(..., ge=1, description="ID vai trò")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email không hợp lệ")
        return email


class AccountUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100, description="Họ và tên")
    gender: Optional[bool] = Field(None, description="Giới tính: false=Nữ, true=Nam")
    birth_of_date: Optional[datetime] = Field(None, description="Ngày sinh")
    role_id: Optional[int] = Field(None, ge=1, description="ID vai trò")
    is_cancel: Optional[bool] = Field(None, description="Vô hiệu hóa tài khoản")
