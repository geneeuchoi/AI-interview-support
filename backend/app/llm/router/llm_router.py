from fastapi import APIRouter, HTTPException, Depends, Request
from app.llm.schema.llm_schema import LLMRequest, LLMResponse
from app.llm.service.llm_service import LLMService
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/llm", tags=["llm"])

def get_llm_service(request: Request) -> LLMService:
    return LLMService(request.app.state.llm_provider)

@router.post("", response_class=StreamingResponse)
async def post_llm(req: LLMRequest,
                   llm_service: LLMService = Depends(get_llm_service)):
    try:
        chunk = llm_service.chat(text=req.text, prompt=req.prompt, model=req.model, language=req.language, max_tokens=req.max_tokens)
        return StreamingResponse(chunk, media_type="text/plain; charset=utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")