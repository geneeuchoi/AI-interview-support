from pydantic import BaseModel, Field

class STTResponse(BaseModel):
    text: str = Field(..., description="Transcribed text")
    model: str = Field(..., description="STT model used")
    language: str = Field(..., description="Language hint")