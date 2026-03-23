from abc import ABC, abstractmethod


class IMailProvider(ABC):

    @abstractmethod
    def send_forgot_password_otp(self, email: str, otp: str) -> None:
        """Gửi OTP quên mật khẩu đến email người dùng."""
        pass
