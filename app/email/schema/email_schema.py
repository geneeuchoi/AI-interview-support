from pydantic import BaseModel, Field

class EmailResponse(BaseModel):
    summary: str = Field(..., description="Summarized text by LLM")
