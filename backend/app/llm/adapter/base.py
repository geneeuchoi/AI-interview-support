from typing import Protocol, Dict, Any, Optional

class LlmProvider(Protocol):
    async def complete(self, system: Optional[str], prompt: str, model: str, extra: Dict[str, Any]) -> str: ...
