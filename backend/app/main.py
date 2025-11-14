from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from app.stt.adapter.stt_adapter import OpenAISttProvider
from app.llm.adapter.llm_adapter import OpenAILlmProvider
from app.email.adapter.email_adapter import EmailSendProvider
from app.audio.adapter.audio_adapter import AudioCompressProvider
from app.web.router.web_router import router as web_router
from app.stt.router.stt_router import router as stt_router
from app.llm.router.llm_router import router as llm_router
from app.email.router.email_router import router as email_router
from app.audio.router.audio_router import router as audio_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.stt_provider = OpenAISttProvider()
    app.state.llm_provider = OpenAILlmProvider()
    app.state.email_provider = EmailSendProvider()
    app.state.audio_provider = AudioCompressProvider()
    yield
app = FastAPI(title="AI interview agent", lifespan=lifespan)

app.include_router(web_router, tags=["web"])
app.include_router(stt_router, prefix="/api", tags=["stt"])
app.include_router(llm_router, prefix="/api", tags=["llm"])
app.include_router(email_router, prefix="/api", tags=["email"])
app.include_router(audio_router, prefix="/api", tags=["audio"])

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
