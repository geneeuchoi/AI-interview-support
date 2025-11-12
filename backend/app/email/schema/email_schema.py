from pydantic import BaseModel, Field

class EmailRequest(BaseModel):
    summary: str = Field(..., description="Summarized text by LLM")
    userName: str = Field(..., description="User name")

class EmailResponse(BaseModel):
    summary: str = Field(..., description="Summarized text by LLM")
