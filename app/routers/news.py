from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.models.schemas import NewsArticle, ClientContext
from app.services.news_ai import summarize_news, news_impact_on_portfolio
from app.core.security import require_internal_key

router = APIRouter(dependencies=[Depends(require_internal_key)])


class SummarizeRequest(BaseModel):
    articles: List[NewsArticle]


class ImpactRequest(BaseModel):
    articles: List[NewsArticle]
    client: ClientContext


class AIResponse(BaseModel):
    result: str


@router.post("/summarize", response_model=AIResponse)
async def summarize(body: SummarizeRequest):
    """Summarize news into key market takeaways."""
    result = summarize_news(body.articles)
    return {"result": result}


@router.post("/impact", response_model=AIResponse)
async def impact(body: ImpactRequest):
    """Explain how today's news affects a specific client's portfolio."""
    result = news_impact_on_portfolio(body.articles, body.client)
    return {"result": result}
