from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Tên đăng nhập")
    password: str = Field(..., min_length=1, max_length=128, description="Mật khẩu")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123",
            }
        }


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(
        ..., min_length=1, max_length=128, description="Mật khẩu hiện tại"
    )
    new_password: str = Field(
        ..., min_length=6, max_length=128, description="Mật khẩu mới"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "admin123",
                "new_password": "new-admin-123",
            }
        }
