from app.email.adapter.email_adapter import EmailSendProvider
from typing import Optional

class EmailService:
    def __init__(self, provider: EmailSendProvider) -> None:
        self.provider = provider

    async def send(self, summary: str, userName: str, audio_data: Optional[bytes] = None, audio_filename: Optional[str] = None):
        await self.provider.by_gmail(
            summary=summary,
            userName=userName,
            audio_data=audio_data,
            audio_filename=audio_filename
        )