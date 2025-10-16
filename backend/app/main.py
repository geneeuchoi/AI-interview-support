from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from app.stt.adapter.stt_adapter import OpenAISttProvider
from app.web.router.web_router import router as web_router
from app.stt.router.stt_router import router as stt_router
# from app.llm.router.llm_router import router as llm_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.stt_provider = OpenAISttProvider()
    yield
app = FastAPI(title="AI interview agent", lifespan=lifespan)

app.include_router(web_router, tags=["WEB"])
app.include_router(stt_router, prefix="/api", tags=["STT"])
# app.include_router(llm.router, prefix="/api", tags=["LLM"])

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
