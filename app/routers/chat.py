from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
from app.models.schemas import ChatMessage, ClientContext
from app.services.ia_client import complete_stream
from app.core.security import require_internal_key

router = APIRouter(dependencies=[Depends(require_internal_key)])

SYSTEM = """You are Finn, an AI financial assistant embedded in Findash.
You help financial advisors understand their clients' portfolios, market movements, and financial concepts.
Be concise, professional, and data-driven. When client context is provided, always personalize your response.
"""


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    client: Optional[ClientContext] = None


def event_generator(system: str, messages: list[dict]):
    for chunk in complete_stream(system, messages):
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    yield "data: [DONE]\n\n"


@router.post("")
async def chat(body: ChatRequest):
    system = SYSTEM
    if body.client:
        symbols = [p.symbol for p in body.client.portfolio]
        system += f"\n\nCurrent client context: {body.client.name}, risk profile: {body.client.riskProfile}."
        if symbols:
            system += f" Portfolio: {', '.join(symbols)}."

    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    return StreamingResponse(
        event_generator(system, messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )