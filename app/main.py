import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.stt.adapter.stt_adapter import OpenAISttProvider
from app.llm.adapter.llm_adapter import OpenAILlmProvider
from app.email.adapter.email_adapter import EmailSendProvider
from app.audio.adapter.audio_adapter import AudioCompressProvider
from app.stt.router.stt_router import router as stt_router
from app.llm.router.llm_router import router as llm_router
from app.email.router.email_router import router as email_router
from app.audio.router.audio_router import router as audio_router
from app.web.router.web_router import router as web_router
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.stt_provider = OpenAISttProvider()
    app.state.llm_provider = OpenAILlmProvider()
    app.state.email_provider = EmailSendProvider()
    app.state.audio_provider = AudioCompressProvider()
    yield
app = FastAPI(title="AI interview agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONT_URL"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.state.templates = templates
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(stt_router, prefix="/api", tags=["stt"])
app.include_router(llm_router, prefix="/api", tags=["llm"])
app.include_router(email_router, prefix="/api", tags=["email"])
app.include_router(audio_router, prefix="/api", tags=["audio"])
app.include_router(web_router, tags=["web"])