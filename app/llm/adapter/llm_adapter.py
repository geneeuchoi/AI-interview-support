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
            agenda: str,
            model: str,
            language: str,
            max_tokens: int,
    ) -> AsyncGenerator[str, None]:
        # TODO: 프롬프트 엔지니어링
        prompt = f"[역할]당신은 일본인 IT 면접관입니다.\n 당신의 회사에서 의뢰한 안건 설명을 참고하여, 유저의 질문에 당신이 만족할 만한 답변을 제시하세요.\n[안건]${agenda} \n[조건]1. 답변은 일본어로 하되, 각각의 한자 옆에 요미가나를 추가해서 일본어에 능숙하지 않은 사용자가 빠르게 읽을 수 있게 도와주세요. 2. 사용자가 보고 그대로 읽을 수 있도록 자연스러우면서도 정중한 구어체로 답변을 제공해주세요. 3. 이때, \"네, 답변해드리겠습니다\"와 같은 말은 제외하고 제가 요구한 사항만 제공해주세요. [중요] 마지막으로 질문하고 싶은 사항이 있냐는 뉘앙스의 유저 응답이 들어올 경우, 안건을 토대로 질문을 만들어주세요."

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
            userName: str,
            agenda: str,
            time: int,
            model: str,
            language: str,
            max_tokens: int,
    ) -> str:

        # TODO: 프롬프트 엔지니어링
        prompt = f"[역할]당신은 유능한 인사 담당자입니다. \n[조건] 1. 메타 정보에 근거해서, 면접 내용을 형식에 맞게 요약해서 제시해주세요. 단, 한국어로 요약 해주세요. 2. 면접은 지원자의 스킬시트를 설명하고 시작하는 경우가 많습니다. 스킬시트를 설명하는 것 같다면, [스킬시트 설명]이라는 소제목 아래에 내용을 정리해주세요. 3. 면접자, 안건은 메타정보 그대로 템플릿에 붙여넣어 주세요. 4. 면접 시간은 초로 주어집니다. 60초를 넘어갈 경우 분, 초로 나누어서 제공해주세요. \n[메타 정보] 면접자: ${userName} 면접 시간:${time}초 안건: ${agenda} \n[형식] 1. 메타 정보: 면접자, 면접 시간 \n2.안건 설명 3.-스킬시트 설명: -질문: -답변: "

        def _call_openai() -> str:
            try:

                response = self.client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text},
                    ],
                    max_output_tokens=max_tokens,
                )

                return response.output_text
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