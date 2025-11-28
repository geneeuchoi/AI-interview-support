from app.llm.adapter.llm_adapter import OpenAILlmProvider
from typing import AsyncGenerator

class LLMService:
    def __init__(self, provider: OpenAILlmProvider) -> None:
        self.provider = provider

    async def chat(self, text: str, agenda: str,
                   model: str, language: str, max_tokens: int) -> AsyncGenerator[str, None]:
        async for chunk in self.provider.qna(text=text,
                                             agenda=agenda,
                                             model=model,
                                             language=language,
                                             max_tokens=max_tokens):
            yield chunk

    async def summary(self, text: str, userName: str, agenda: str, time: int,
                      model: str, language: str, max_tokens: int) -> str:
        summary = await self.provider.summary(text=text,
                                              userName=userName,
                                              agenda=agenda,
                                              time=time,
                                              model=model,
                                              language=language,
                                              max_tokens=max_tokens)
        return summary