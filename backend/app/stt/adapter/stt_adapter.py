import anyio
import tempfile
import os
from fastapi import UploadFile
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

class OpenAISttProvider:
    # Optional[str]: 타입 힌트. 문자열 또는 None.
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)

    async def transcribe_audio(
        self,
        audio: UploadFile,
        model: str = "gpt-4o-mini-transcribe",
        language: str = "ja",
    ) -> str: # 타입 힌트. 반환값이 str.

        suffix = f".{(audio.filename or 'audio').split('.')[-1]}"
        if len(suffix) > 6 or "/" in suffix or "\\" in suffix:
            suffix = ".wav"

        async with anyio.create_task_group() as tg:
            tmp_path = await tg.start(self._save_to_tmp, audio, suffix)

        def _call_openai() -> str:
            with open(tmp_path, "rb") as f:
                resp = self.client.audio.transcriptions.create(
                    model=model,
                    file=f,
                    language=language,
                    response_format="text",  # text / json 등
                )
                # response_format="text"면 str이 오고, json이면 obj.text 사용
                return resp if isinstance(resp, str) else resp.text

        try:
            text: str = await anyio.to_thread.run_sync(_call_openai)
            # 최종값 리턴
            return text.strip()
        finally:
            # 임시 파일 정리
            import os
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    async def _save_to_tmp(self, task_status, upload: UploadFile, suffix: str) -> None:
        # anyio task nursery와 호환되는 초기화 패턴
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            # 큰 파일도 안전하게 chunk 단위로 복사
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
            tmp_path = tmp.name
        task_status.started(tmp_path)
