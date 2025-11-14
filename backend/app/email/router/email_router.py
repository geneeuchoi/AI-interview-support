from fastapi import APIRouter, HTTPException, Depends, Request, Form, UploadFile, File
from app.email.schema.email_schema import EmailResponse
from app.email.service.email_service import EmailService
from typing import Optional

router = APIRouter(prefix="/email", tags=["email"])

def get_email_service(request: Request) -> EmailService:
    return EmailService(request.app.state.email_provider)

@router.post("", response_model=EmailResponse)
async def post_email(
    summary: str = Form(...),
    userName: str = Form(...),
    audio: Optional[UploadFile] = File(None),
    email_service: EmailService = Depends(get_email_service)
):
    try:
        audio_data = None
        audio_filename = None
        if audio:
            audio_data = await audio.read()
            audio_filename = audio.filename

        await email_service.send(
            summary=summary,
            userName=userName,
            audio_data=audio_data,
            audio_filename=audio_filename
        )
        return EmailResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email send failed: {e}")