import logging
import smtplib
from email.message import EmailMessage

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


class SMTPProvider(IMailProvider):
    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        if not settings.smtp_host:
            raise ValueError("SMTP_HOST chưa được cấu hình")
        if not settings.smtp_sender_email:
            raise ValueError("SMTP_SENDER_EMAIL chưa được cấu hình")

        security = settings.smtp_security.strip().lower()
        if security not in {"tls", "ssl", "none"}:
            raise ValueError("SMTP_SECURITY phải là một trong: tls, ssl, none")

        if settings.smtp_username and not settings.smtp_password:
            raise ValueError("SMTP_PASSWORD chưa được cấu hình")

    @staticmethod
    def _build_message(to_email: str, otp: str) -> EmailMessage:
        message = EmailMessage()
        sender_name = settings.smtp_sender_name.strip()
        if sender_name:
            message["From"] = f"{sender_name} <{settings.smtp_sender_email}>"
        else:
            message["From"] = settings.smtp_sender_email
        message["To"] = to_email
        message["Subject"] = "Mã xác thực quên mật khẩu"
        message.set_content(
            (
                f"Mã OTP của bạn là: {otp}. "
                f"Mã có hiệu lực trong {settings.forgot_password_otp_ttl_seconds // 60} phút."
            )
        )
        return message

    @staticmethod
    def _safe_local_hostname() -> str:
        # Tránh lỗi EHLO argument invalid trên một số máy Windows có hostname chứa ký tự không hợp lệ
        return "localhost"

    def _send_with_tls_or_plain(self, message: EmailMessage, use_tls: bool) -> None:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
            local_hostname=self._safe_local_hostname(),
        ) as server:
            server.ehlo(self._safe_local_hostname())
            if use_tls:
                server.starttls()
                server.ehlo(self._safe_local_hostname())

            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)

            server.send_message(message)

    def _send_with_ssl(self, message: EmailMessage) -> None:
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
            local_hostname=self._safe_local_hostname(),
        ) as server:
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)

    def send_forgot_password_otp(self, email: str, otp: str) -> None:
        message = self._build_message(email, otp)
        security = settings.smtp_security.strip().lower()

        try:
            self.logger.info(
                "Sending forgot-password OTP via SMTP host=%s port=%s security=%s to=%s",
                settings.smtp_host,
                settings.smtp_port,
                security,
                email,
            )
            if security == "ssl":
                self._send_with_ssl(message)
            else:
                self._send_with_tls_or_plain(message, use_tls=(security == "tls"))

            self.logger.info("Sent forgot-password OTP email via SMTP to %s", email)
        except Exception as exc:
            self.logger.exception(
                "Failed to send forgot-password OTP via SMTP to %s: %s",
                email,
                str(exc),
            )


def create_mail_provider() -> IMailProvider:
    logger = logging.getLogger(__name__)
    provider_type = settings.mail_provider_type.strip().lower()
    if provider_type == "mailtrap":
        logger.info("Using mail provider: mailtrap")
        return MailtrapProvider()
    if provider_type == "smtp":
        logger.info("Using mail provider: smtp")
        return SMTPProvider()
    raise ValueError(f"MAIL_PROVIDER_TYPE không được hỗ trợ: {settings.mail_provider_type}")
