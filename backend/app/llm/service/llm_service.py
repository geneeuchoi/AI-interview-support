from app.llm.adapter.llm_adapter import OpenAILlmProvider

class LLMService:
    def __init__(self, provider: OpenAILlmProvider) -> None:
        self.provider = provider

    async def chat(self, text: str, prompt: str, model: str, language: str, max_tokens: str) -> str:
        text = await self.provider.qna(text=text, prompt=prompt, model=model, language=language, max_tokens=max_tokens)
        return text
