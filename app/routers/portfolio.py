from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.models.schemas import ClientContext, StockQuote
from app.services.portfolio_ai import analyze_portfolio, suggest_rebalance
from app.core.security import require_internal_key

router = APIRouter(dependencies=[Depends(require_internal_key)])


class AnalyzeRequest(BaseModel):
    client: ClientContext
    quotes: List[StockQuote]


class AIResponse(BaseModel):
    result: str


@router.post("/analyze", response_model=AIResponse)
async def analyze(body: AnalyzeRequest):
    """Full portfolio analysis with live quotes."""
    result = analyze_portfolio(body.client, body.quotes)
    return {"result": result}


@router.post("/rebalance", response_model=AIResponse)
async def rebalance(body: AnalyzeRequest):
    """Rebalancing suggestion based on risk profile and current weights."""
    result = suggest_rebalance(body.client, body.quotes)
    return {"result": result}
