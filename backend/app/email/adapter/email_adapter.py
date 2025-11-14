import os
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.utils import formataddr
from datetime import datetime
import aiosmtplib
from typing import Optional


class EmailSendProvider:
    def __init__(self) -> None:
        self.gmail_root = os.getenv("GMAIL_ROOT").strip()
        self.gmail_app_password = os.getenv("GMAIL_APP_PASSWORD").strip()
        self.mail_subject = os.getenv("MAIL_SUBJECT")
        self.mail_sender_name = os.getenv("MAIL_SENDER_NAME")
        self.mail_recipient = os.getenv("MAIL_RECIPIENT")

    async def by_gmail(self, summary: str, userName: str, audio_data: Optional[bytes] = None, audio_filename: Optional[str] = None) -> None:
        msg = MIMEMultipart()
        msg["Subject"] = f"{self.mail_subject} {datetime.now().strftime('%Y년 %-m월 %-d일')} {userName}님 면접 요약"
        msg["From"] = formataddr((self.mail_sender_name, self.gmail_root))
        msg["To"] = self.mail_recipient

        body = MIMEText(summary, _charset="utf-8")
        msg.attach(body)

        if audio_data and audio_filename:
            audio_attachment = MIMEAudio(audio_data, _subtype="mpeg")
            audio_attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=audio_filename
            )
            msg.attach(audio_attachment)

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