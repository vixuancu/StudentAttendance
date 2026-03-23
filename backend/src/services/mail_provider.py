import logging

from src.config.settings import settings
from src.services.interfaces.i_mail_provider import IMailProvider


class MailtrapProvider(IMailProvider):
    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        if not settings.mailtrap_api_key:
            raise ValueError("MAILTRAP_API_KEY chưa được cấu hình")

        import mailtrap as mt

        self._mt = mt
        client_kwargs = {
            "token": settings.mailtrap_api_key,
            "sandbox": settings.mailtrap_sandbox,
        }
        if settings.mailtrap_sandbox and settings.mailtrap_inbox_id is not None:
            client_kwargs["inbox_id"] = settings.mailtrap_inbox_id

        self.client = self._mt.MailtrapClient(**client_kwargs)

    def send_forgot_password_otp(self, email: str, otp: str) -> None:
        mail = self._mt.Mail(
            sender=self._mt.Address(
                email=settings.mailtrap_sender_email,
                name=settings.mailtrap_sender_name,
            ),
            to=[self._mt.Address(email=email)],
            subject="Mã xác thực quên mật khẩu",
            text=(
                f"Mã OTP của bạn là: {otp}. "
                f"Mã có hiệu lực trong {settings.forgot_password_otp_ttl_seconds // 60} phút."
            ),
            category="Forgot Password",
        )
        try:
            self.client.send(mail)
            self.logger.info("Sent forgot-password OTP email to %s", email)
        except Exception:
            self.logger.exception("Failed to send forgot-password OTP to %s", email)


def create_mail_provider() -> IMailProvider:
    provider_type = settings.mail_provider_type.strip().lower()
    if provider_type == "mailtrap":
        return MailtrapProvider()
    raise ValueError(f"MAIL_PROVIDER_TYPE không được hỗ trợ: {settings.mail_provider_type}")
