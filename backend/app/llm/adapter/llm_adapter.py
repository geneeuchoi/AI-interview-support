import os
from typing import AsyncGenerator, Optional, Iterable
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
            prompt: str,
            model: str,
            language: str,
            max_tokens: int,
    ) -> AsyncGenerator[str, None]:

        # TODO: 프롬프트 엔지니어링
        def _call_openai() -> Iterable:
            return self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text},
                    ],
                    max_tokens=max_tokens,
                    stream=True,
            )

        send, recv = anyio.create_memory_object_stream[str](max_buffer_size=0)

        async def producer():
            try:
                def run_sync():
                    stream = _call_openai()
                    for chunk in stream:
                        for choice in chunk.choices:
                            delta = choice.delta
                            content = getattr(delta, "content", None)
                            if content:
                                # 스레드 → async로 안전하게 전송
                                anyio.from_thread.run(send.send, content)

                await anyio.to_thread.run_sync(run_sync)
            except Exception as e:
                print(f"[LLM ERROR] {e}")
            finally:
                await send.aclose()


        async with anyio.create_task_group() as tg:
            tg.start_soon(producer)
            async with recv:
                async for token in recv:
                    yield token
