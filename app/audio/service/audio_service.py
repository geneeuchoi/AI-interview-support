from app.audio.adapter.audio_adapter import AudioCompressProvider
from fastapi import UploadFile

class AudioService:
    def __init__(self, provider: AudioCompressProvider) -> None:
        self.provider = provider

    async def compress(self, audio: UploadFile) -> bytes:
        compressed_audio = await self.provider.compress_audio(audio)
        return compressed_audio