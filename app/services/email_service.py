import smtplib
from email.message import EmailMessage
from typing import List, Optional

from ..config import Config


class EmailService:
    """Servicio sencillo para envío de correos SMTP."""
    BLOCKED_DOMAINS = {"admin.com", "localhost", "localdomain", "example.com", "test.com"}

    def __init__(self) -> None:
        self.host = Config.SMTP_HOST
        self.port = Config.SMTP_PORT
        self.user = Config.SMTP_USER
        self.password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM or self.user
        self.use_tls = Config.SMTP_USE_TLS

    @property
    def enabled(self) -> bool:
        return bool(self.host and self.port and self.user and self.password and self.from_email)

    def _is_valid_email(self, email: str) -> bool:
        if not email or "@" not in email or "." not in email:
            return False
        try:
            local, domain = email.rsplit("@", 1)
        except ValueError:
            return False
        if not local.strip() or not domain.strip():
            return False
        if domain.lower() in self.BLOCKED_DOMAINS:
            return False
        return True

    def send_email(self, to_emails: List[str], subject: str, body: str) -> bool:
        """Envía un correo de texto plano. Retorna True si se envió, False si no."""
        if not self.enabled:
            return False
        if not to_emails:
            return False
        valid_recipients = [e for e in to_emails if self._is_valid_email(e)]
        if not valid_recipients:
            return False

        msg = EmailMessage()
        msg["From"] = self.from_email
        msg["To"] = ", ".join(valid_recipients)
        msg["Subject"] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            return True
        except Exception:
            # Silenciar errores para no romper el flujo principal
            return False
