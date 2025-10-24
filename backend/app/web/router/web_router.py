from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/stt-test", response_class=HTMLResponse)
async def stt_test(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/email-test", response_class=HTMLResponse)
async def email_test(request: Request):
    return templates.TemplateResponse("email.html", {"request": request})

