from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from app.stt.schema.stt_schema import STTResponse
from app.stt.service.stt_service import STTService

router = APIRouter(prefix="/stt", tags=["stt"])

def get_stt_service(request: Request) -> STTService:
    return STTService(request.app.state.stt_provider)

@router.post("", response_model=STTResponse)
async def post_stt(
    audio: UploadFile = File(...),
    language: str = Form(...),
    model: str = Form(...),
    service: STTService = Depends(get_stt_service)):
    try:
        text = await service.transcribe(audio, model=model, language=language)
        return STTResponse(text=text, model=model, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")