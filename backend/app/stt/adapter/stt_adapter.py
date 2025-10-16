import anyio
import tempfile
import os
from fastapi import UploadFile
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# stt 가능한 확장자
# File uploads are currently limited to 25 MB,
# and the following input file types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm.
# Known speaker reference clips for diarization accept the same formats when provided as data URLs.
# https://platform.openai.com/docs/guides/speech-to-text

# Content-Type -> 확장자 매핑 (webm 확실히 커버)
EXT_BY_CONTENT_TYPE = {
    "audio/webm": ".webm",
    "video/webm": ".webm",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mp4": ".m4a",
    "audio/aac": ".aac",
    "audio/ogg": ".ogg",
    "video/mp4": ".mp4",
}

class OpenAISttProvider:
    # Optional[str]: 타입 힌트. 문자열 또는 None.
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    async def transcribe_audio(
        self,
        audio: UploadFile,
        model: str,
        language: str
    ) -> str: # 타입 힌트. 반환값이 str.

        # content_type 우선 확장자 결정
        ct = (audio.content_type or "").lower()
        suffix = EXT_BY_CONTENT_TYPE.get(ct)

        if not suffix:
            fname = (audio.filename or "").lower()
            if fname.endswith(".webm"):
                suffix = ".webm"
            elif fname.endswith(".wav"):
                suffix = ".wav"
            elif fname.endswith(".mp3"):
                suffix = ".mp3"
            elif fname.endswith(".m4a"):
                suffix = ".m4a"
            else:
                # 최종 폴백: webm 추정 시 webm, 그 외 wav
                suffix = ".webm" if ("webm" in fname or "webm" in ct) else ".wav"

        tmp_path: Optional[str] = None

        async with anyio.create_task_group() as tg:
            tmp_path = await tg.start(self._save_to_tmp, audio, suffix)

        def _call_openai() -> str:
            with open(tmp_path, "rb") as f:
                # response_format 생략(기본 json) -> 호환성 ↑
                resp = self.client.audio.transcriptions.create(
                    model=model,
                    file=f,
                    language=language,
                )
                # SDK에 따라 obj.text 또는 dict["text"] 형태
                text = getattr(resp, "text", None)
                if text is None and isinstance(resp, dict):
                    text = resp.get("text")
                if not text and isinstance(resp, str):
                    text = resp
                return (text or "").strip()

        try:
            return await anyio.to_thread.run_sync(_call_openai)
        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        # anyio 정석 시그니처: task_status는 keyword-only

    async def _save_to_tmp(
            self,
            upload: UploadFile,
            suffix: str,
            *,
            task_status=anyio.TASK_STATUS_IGNORED
    ) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            path = tmp.name
        task_status.started(path)