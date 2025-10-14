from fastapi import APIRouter, UploadFile, File
from app.services.stt_service import transcribe_and_respond

router = APIRouter()

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    text = await transcribe_and_respond(file)
    return {"text": text}
