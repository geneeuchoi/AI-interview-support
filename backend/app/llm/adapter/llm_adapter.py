import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import anyio

# TODO: 배포시 로그 삭제
os.environ.setdefault("OPENAI_LOG", "debug")
load_dotenv(find_dotenv(usecwd=True))

class OpenAILlmProvider:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    async def qna(
            self,
            text: str,
            prompt: Optional[str],
            model: str = "gpt-4o-mini",
            language: str = "ja",
            max_tokens: int = 512,
    ) -> str:

        # TODO: 프롬프트 엔지니어링
        def _call_openai() -> str:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                max_tokens=max_tokens,
            )

            reply = (
                response.choices[0].message.content.strip()
                if response and response.choices
                else ""
            )
            return reply

        # 실제 OpenAI 호출은 스레드 풀에서 실행
        try:
            reply_text = await anyio.to_thread.run_sync(_call_openai)
            return reply_text
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return f"LLM 요청 중 오류가 발생했습니다: {e}"