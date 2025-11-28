from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
async def root_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("meta_info.html", {"request": request})

@router.get("/prototype", response_class=HTMLResponse)
async def prototype_test(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("prototype.html", {"request": request})

@router.get("/meta_info", response_class=HTMLResponse)
async def meta_info(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("meta_info.html", {"request": request})