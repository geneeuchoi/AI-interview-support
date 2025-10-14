from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import stt


# Flask의 app = Flask(__name__)과 비슷한 역할
# 이 객체가 실제 서버의 핵심
# title은 Swagger 문서(/docs)에 표시되는 앱 이름
app = FastAPI(title="AI interview agent")

# Tailwind 결과 파일(static) 연결
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 템플릿 연결
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# api 등록
app.include_router(stt.router, prefix="/stt", tags=["STT"])
