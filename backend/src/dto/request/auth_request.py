from pydantic import BaseModel, Field, field_validator


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


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, description="Email đăng ký")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email không hợp lệ")
        return email


class ForgotPasswordConfirmRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255, description="Email đăng ký")
    otp: str = Field(..., min_length=6, max_length=6, description="Mã OTP 6 số")
    new_password: str = Field(..., min_length=6, max_length=128, description="Mật khẩu mới")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email không hợp lệ")
        return email

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        otp = value.strip()
        if not otp.isdigit() or len(otp) != 6:
            raise ValueError("Mã OTP phải gồm 6 chữ số")
        return otp
