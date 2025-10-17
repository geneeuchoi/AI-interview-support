from fastapi import APIRouter, HTTPException, Depends, Request
from app.llm.schema.llm_schema import LLMRequest, LLMResponse
from app.llm.service.llm_service import LLMService

router = APIRouter(prefix="/llm", tags=["llm"])
print("llm")

def get_llm_service(request: Request) -> LLMService:
    return LLMService(request.app.state.llm_provider)

@router.post("", response_model=LLMResponse)
async def post_llm(req: LLMRequest,
                   llm_service: LLMService = Depends(get_llm_service)):
    try:
        text = await llm_service.chat(text=req.text, prompt=req.prompt, model=req.model, language=req.language, max_tokens=req.max_tokens)
        return LLMResponse(text=text, model=req.model, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")