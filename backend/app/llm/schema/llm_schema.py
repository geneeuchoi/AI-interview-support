from pydantic import BaseModel, Field
from typing import Optional

class LLMRequest(BaseModel):
    text: str = Field(..., description="STT result text")
    userName: Optional[str] = Field(None, description="User name")
    agenda: Optional[str] = Field(None, description="Agenda user entered")
    time: Optional[int] = Field(None, description="Interview time")
    model: str = Field(..., description="LLM model")
    language: str = Field("ja", description="Language hint")
    max_tokens: Optional[int] = 512

class LLMResponse(BaseModel):
    text: str = Field(..., description="Answer text")
    model: str = Field(..., description="LLM model used")
    language: str = Field(..., description="Language hint")