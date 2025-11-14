from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/prototype", response_class=HTMLResponse)
async def prototype_test(request: Request):
    return templates.TemplateResponse("prototype.html", {"request": request})

@router.get("/meta_info", response_class=HTMLResponse)
async def meta_info(request: Request):
    return templates.TemplateResponse("meta_info.html", {"request": request})