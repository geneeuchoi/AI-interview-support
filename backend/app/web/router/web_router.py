from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/prototype", response_class=HTMLResponse)
async def email_test(request: Request):
    return templates.TemplateResponse("prototype.html", {"request": request})

