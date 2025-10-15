from fastapi import APIRouter, UploadFile, File, Form
from app.stt.schemas.stt_schema import STTResponse
from app.stt.service.stt_service import STTService
from app.stt.adapter.stt_adapter import OpenAISttProvider

router = APIRouter(prefix="/api", tags=["stt"])

_provider = OpenAISttProvider()
_service = STTService(_provider)

@router.post("/stt", response_model=STTResponse)
async def stt_endpoint(
    audio: UploadFile = File(..., description="Audio file"),
    language: str = Form("ja"),
    model: str = Form("gpt-4o-mini-transcribe")
):
    try:
        text = await _service.transcribe(audio, model=model, language=language)
        return STTResponse(text=text, model=model, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")