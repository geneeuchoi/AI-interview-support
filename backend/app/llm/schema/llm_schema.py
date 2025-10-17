from pydantic import BaseModel, Field
from typing import Optional

class LLMRequest(BaseModel):
    text: str = Field(..., description="STT result text")
    prompt: Optional[str] = Field(None, description="System prompt")
    model: str = Field("gpt-4o-mini", description="LLM model")
    language: str = Field("ja", description="Language hint")
    max_tokens: Optional[int] = 512

class LLMResponse(BaseModel):
    text: str = Field(..., description="Answer text")
    model: str = Field(..., description="LLM model used")
    language: str = Field(..., description="Language hint")