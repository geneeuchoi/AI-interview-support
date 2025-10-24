from fastapi import APIRouter, HTTPException, Depends, Request
from app.email.schema.email_schema import EmailRequest, EmailResponse
from app.email.service.email_service import EmailService

router = APIRouter(prefix="/email", tags=["email"])

def get_email_service(request: Request) -> EmailService:
    return EmailService(request.app.state.email_provider)

@router.post("", response_model=EmailResponse)
async def post_email(req: EmailRequest,
                   email_service: EmailService = Depends(get_email_service)):
    try:
        await email_service.send(summary=req.summary)
        return EmailResponse(summary=req.summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email send failed: {e}")