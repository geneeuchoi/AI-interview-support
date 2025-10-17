import os, tempfile, anyio
from fastapi import UploadFile
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# TODO: 배포시 로그 삭제
os.environ.setdefault("OPENAI_LOG", "debug")
load_dotenv(find_dotenv(usecwd=True))

EXT_BY_CONTENT_TYPE = {
    "audio/webm": ".webm", "video/webm": ".webm",
    "audio/mpeg": ".mp3", "audio/mp3": ".mp3",
    "audio/wav": ".wav", "audio/x-wav": ".wav",
    "audio/mp4": ".m4a", "audio/aac": ".aac", "audio/ogg": ".ogg",
    "video/mp4": ".mp4",
}

def _guess_suffix(filename: str | None, content_type: str | None) -> str:
    ct = (content_type or "").lower().split(";", 1)[0].strip()
    if ct in EXT_BY_CONTENT_TYPE:
        return EXT_BY_CONTENT_TYPE[ct]
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    return ".webm"


class OpenAISttProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    # 코루틴 함수: 비동기 처리
    async def transcribe_audio(self, audio: UploadFile, model: str, language: str) -> str:

        await audio.seek(0) # 오디오 포인터를 앞으로 돌림
        suffix = _guess_suffix(audio.filename, audio.content_type)

        async def _save(upload: UploadFile, sfx: str, *, task_status=anyio.TASK_STATUS_IGNORED):
            with tempfile.NamedTemporaryFile(delete=False, suffix=sfx) as tmp:
                size = 0
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    tmp.write(chunk)
                    size += len(chunk)
                path = tmp.name
            task_status.started(path)

        async with anyio.create_task_group() as tg:
            tmp_path = await tg.start(_save, audio, suffix)

        def _call_openai() -> str:
            print("[OpenAISttProvider] calling OpenAI...")
            try:
                with open(tmp_path, "rb") as f:
                    resp = self.client.audio.transcriptions.create(
                        model=model,
                        file=f,
                        language=language,
                    )
                text = getattr(resp, "text", None)
                if text is None and isinstance(resp, dict):
                    text = resp.get("text")
                if not text and isinstance(resp, str):
                    text = resp
                print("[OpenAISttProvider] OpenAI OK")
                return (text or "").strip()
            except Exception as e:
                print(f"[OpenAISttProvider] OpenAI error: {e!r}")
                raise

        try:
            return await anyio.to_thread.run_sync(_call_openai)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
