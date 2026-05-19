from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── Matches Prisma Position model ──────────────────────────────────────────
class Position(BaseModel):
    id: str
    symbol: str
    name: str
    quantity: float
    avgBuyPrice: float
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


# ── Matches Prisma Transaction model ───────────────────────────────────────
class Transaction(BaseModel):
    id: str
    symbol: str
    name: str
    type: str           # "buy" | "sell"
    quantity: float
    price: float
    date: Optional[datetime] = None


# ── Matches Prisma Client model (subset relevant to AI) ────────────────────
class ClientContext(BaseModel):
    id: str
    name: str
    riskProfile: Optional[str] = "moderate"   # conservative | moderate | aggressive
    portfolio: List[Position] = []
    transactions: List[Transaction] = []


# ── Live quote passed in from the Node backend ─────────────────────────────
class StockQuote(BaseModel):
    symbol: str
    name: str
    price: float
    previousClose: float
    change: float
    changePercent: float
    currency: Optional[str] = "USD"


# ── News article passed in from the Node backend ───────────────────────────
class NewsArticle(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    publishedAt: str


# ── Chat message ────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str       # "user" | "assistant"
    content: str
