from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from fastapi.responses import Response
from app.audio.service.audio_service import AudioService

router = APIRouter(prefix="/audio", tags=["audio"])

def get_audio_service(request: Request) -> AudioService:
    return AudioService(request.app.state.audio_provider)

@router.post("")
async def post_audio_compress(audio: UploadFile = File(...),
                   audio_service: AudioService = Depends(get_audio_service)):
    try:
        compressed_audio = await audio_service.compress(audio)

        return Response(
            content=compressed_audio,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=compressed_{audio.filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio compress failed: {e}")