import os
import asyncio
from email.mime.text import MIMEText
from email.utils import formataddr
import aiosmtplib


class EmailSendProvider:
    def __init__(self) -> None:
        self.gmail_root = os.getenv("GMAIL_ROOT").strip()
        self.gmail_app_password = os.getenv("GMAIL_APP_PASSWORD").strip()
        self.mail_subject = os.getenv("MAIL_SUBJECT")
        self.mail_sender_name = os.getenv("MAIL_SENDER_NAME")
        self.mail_recipient = os.getenv("MAIL_RECIPIENT")

    async def by_gmail(self, summary: str) -> None:
        msg = MIMEText(summary, _charset="utf-8")
        msg["Subject"] = self.mail_subject
        msg["From"] = formataddr((self.mail_sender_name, self.gmail_root))
        msg["To"] = self.mail_recipient

        smtp_kwargs = {
            "hostname": "smtp.gmail.com",
            "port": 587,
            "start_tls": True,
            "username": self.gmail_root,
            "password": self.gmail_app_password,
            "timeout": 30,
        }

        try:
            await aiosmtplib.send(msg, **smtp_kwargs)
        except aiosmtplib.errors.SMTPException as e:
            raise RuntimeError(f"Gmail 전송 실패: {e}") from e