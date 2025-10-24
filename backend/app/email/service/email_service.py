from app.email.adapter.email_adapter import EmailSendProvider

class EmailService:
    def __init__(self, provider: EmailSendProvider) -> None:
        self.provider = provider

    async def send(self, summary):
        await self.provider.by_gmail(summary=summary)