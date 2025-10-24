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
            model: str,
            language: str,
            max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        # TODO: 프롬프트 엔지니어링
        prompt = "당신은 일본인 IT 면접관입니다.\n유저의 질문에 당신이 만족할 만한 답변을 제시하세요.\n단, 답변은 일본어로 하되, 각각의 한자 옆에 요미가나를 추가해서 일본어에 능숙하지 않은 사용자가 빠르게 읽을 수 있게 도와주세요."

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
                print(f"[OpenAILlmProvider Qna] {e}")
            finally:
                await send.aclose()


        async with anyio.create_task_group() as tg:
            tg.start_soon(producer)
            async with recv:
                async for token in recv:
                    yield token


    async def summary(
            self,
            text: str,
            model: str,
            language: str,
            max_tokens: int,
    ) -> str:

        # TODO: 프롬프트 엔지니어링
        prompt = "당신은 요약이 특기입니다. 면접 내용을 요약해서 텍스트로 제시해주세요. 또한 면접에 대한 총평과 피드백도 내려주세요."

        def _call_openai() -> str:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text},
                    ],
                    max_completion_tokens=max_tokens,
                )
                reply = (response.choices[0].message.content or "").strip()

                print(f"[OpenAILlmProvider] reply: {reply}")
                return reply
            except Exception as e:
                # OpenAI SDK 에러 객체에 response가 붙어오는 경우가 있음
                detail = getattr(e, "response", None)
                print("[OpenAI ERROR]", e)
                if detail is not None:
                    try:
                        print("[OpenAI ERROR BODY]", detail.json())
                    except Exception:
                        print("[OpenAI ERROR BODY RAW]", detail.text)
                raise

        try:
            return await anyio.to_thread.run_sync(_call_openai)
        except Exception as e:
            print(f"[OpenAILlmProvider summary] {e}")
            return f"LLM 요청 중 오류가 발생했습니다: {e}"