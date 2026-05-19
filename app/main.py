from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import portfolio, news, chat

app = FastAPI(
    title="Findash AI Service",
    description="AI microservice for the Findash financial dashboard",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router, prefix="/ai/portfolio", tags=["Portfolio AI"])
app.include_router(news.router, prefix="/ai/news", tags=["News AI"])
app.include_router(chat.router, prefix="/ai/chat", tags=["Chat"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "findash-ai"}
