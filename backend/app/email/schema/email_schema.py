from pydantic import BaseModel, Field

class EmailRequest(BaseModel):
    summary: str = Field(..., description="Summarized text by LLM")

class EmailResponse(BaseModel):
    summary: str = Field(..., description="Summarized text by LLM")
