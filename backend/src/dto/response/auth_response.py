from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    email: str
    role_id: int
    role_name: str | None = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: TokenResponse
    user: UserInfoResponse
