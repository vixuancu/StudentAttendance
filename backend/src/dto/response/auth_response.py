from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    token: TokenResponse
    user: UserInfoResponse
