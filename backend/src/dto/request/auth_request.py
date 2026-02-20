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
