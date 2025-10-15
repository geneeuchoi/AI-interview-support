from app.stt.adapter.stt_adapter import OpenAISttProvider

class STTService:
    def __init__(self, provider: OpenAISttProvider) -> None:
        self.provider = provider

    async def transcribe(self, audio: UploadFile, model: str, language: str) -> str:
        text = await self.provider.transcribe_audio(audio, model=model, language=language)
        return text
