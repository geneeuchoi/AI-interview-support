from pydantic import BaseModel, Field
from fastapi import Form

class STTRequest(BaseModel):
    model: str = Field("gpt-4o-mini-transcribe", description="STT model")
    language: str = Field("ja", description="Language hint")

    @classmethod
    def as_form(
        cls,
        model: str = Form("gpt-4o-mini-transcribe"),
        language: str = Form("ja"),
    ) -> "STTRequest":
        return cls(model=model, language=language)



class STTResponse(BaseModel):
    text: str = Field(..., description="Transcribed text")
    model: str = Field(..., description="STT model used")
    language: str = Field(..., description="Language hint")
