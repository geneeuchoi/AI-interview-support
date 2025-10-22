from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from app.stt.schema.stt_schema import STTResponse, STTRequest
from app.stt.service.stt_service import STTService

router = APIRouter(prefix="/stt", tags=["stt"])

def get_stt_service(request: Request) -> STTService:
    return STTService(request.app.state.stt_provider)

@router.post("", response_model=STTResponse)
async def post_stt(audio: UploadFile = File(...),
                   req: STTRequest = Depends(STTRequest.as_form),
                   stt_service: STTService = Depends(get_stt_service)):

    try:
        text = await stt_service.transcribe(audio, model=req.model, language=req.language)
        return STTResponse(text=text, model=req.model, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")
