from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.models.schemas import ChatMessage, ClientContext
from app.services.ia_client import complete
from app.core.security import require_internal_key

router = APIRouter(dependencies=[Depends(require_internal_key)])

SYSTEM = """You are Finn, an AI financial assistant embedded in Findash.
You help financial advisors understand their clients' portfolios, market movements, and financial concepts.
Be concise, professional, and data-driven. When client context is provided, always personalize your response.
"""


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    client: Optional[ClientContext] = None   # optional context for personalization


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Multi-turn chat with optional client context.
    The Node backend maintains conversation history and passes it each request.
    """
    system = SYSTEM
    if body.client:
        symbols = [p.symbol for p in body.client.portfolio]
        system += f"\n\nCurrent client context: {body.client.name}, risk profile: {body.client.riskProfile}."
        if symbols:
            system += f" Portfolio: {', '.join(symbols)}."

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    reply = complete(system, messages, max_tokens=1024)
    return {"reply": reply}
