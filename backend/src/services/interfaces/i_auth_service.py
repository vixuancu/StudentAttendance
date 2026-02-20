from abc import ABC, abstractmethod

from src.db.models.user import User
from src.dto.request.auth_request import LoginRequest


class IAuthService(ABC):
    """Interface cho AuthService – xử lý xác thực."""

    @abstractmethod
    async def login(self, request: LoginRequest) -> tuple[User, str]:
        """
        Xác thực user và trả về (User, access_token).
        Raise UnauthorizedException nếu sai credentials.
        """
        pass
