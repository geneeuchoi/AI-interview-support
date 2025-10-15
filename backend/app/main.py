from fastapi import FastAPI
app = FastAPI(title="AI interview agent")

app.include_router(web.router, prefix="/web", tags=["WEB"])
app.include_router(stt.router, prefix="/stt", tags=["STT"])
app.include_router(llm.router, prefix="/llm", tags=["LLM"])