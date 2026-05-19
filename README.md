# findash-ai

Python AI microservice for the [Findash](https://github.com/MnicG/findash) financial dashboard.
Built with **FastAPI**

---

## What it does

| Endpoint | What it delivers |
|---|---|
| `POST /ai/portfolio/analyze` | Full portfolio analysis with live P&L and today's movers |
| `POST /ai/portfolio/rebalance` | Rebalancing suggestion based on client risk profile |
| `POST /ai/news/summarize` | Key market takeaways from a list of news articles |
| `POST /ai/news/impact` | How today's news affects a specific client's portfolio |
| `POST /ai/chat` | Multi-turn chat with optional client context (conversational assistant "Finn") |

All endpoints are protected by a shared `X-Internal-Key` header — only your Node backend calls them.

---

## Setup

```bash
cp .env.example .env
# fill in CHUTES_API_KEY and INTERNAL_API_KEY

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs

---

## Integration with the Node backend

Add a helper in `backend/src/utils/aiClient.ts`:

```typescript
import axios from "axios";

const ai = axios.create({
  baseURL: process.env.AI_SERVICE_URL ?? "http://localhost:8000",
  headers: { "X-Internal-Key": process.env.INTERNAL_API_KEY },
});

export default ai;
```

Then call it from any service, e.g. in `client.service.ts`:

```typescript
import ai from "../../utils/aiClient";

async analyzePortfolio(clientId: string, userId: string) {
  const client = await this.getById(clientId, userId);
  const positions = await this.getPositions(clientId, userId);
  const quotes = await Promise.all(
    positions.map(p => stocksService.getQuote(p.symbol))
  );
  const { data } = await ai.post("/ai/portfolio/analyze", {
    client: { ...client, portfolio: positions },
    quotes,
  });
  return data.result;
}
```

---

## Project structure

```
findash-ai/
├── app/
│   ├── main.py              # FastAPI app + CORS + routers
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings, reads .env)
│   │   └── security.py      # X-Internal-Key guard
│   ├── models/
│   │   └── schemas.py       # Pydantic models mirroring Prisma schema
│   ├── services/
│   │   ├── ia_client.py     # Thin SDK wrapper
│   │   ├── portfolio_ai.py  # Portfolio analysis & rebalancing logic
│   │   └── news_ai.py       # News summarization & portfolio impact
│   └── routers/
│       ├── portfolio.py
│       ├── news.py
│       └── chat.py
├── requirements.txt
├── Dockerfile
├── docker-compose.ai.yml    # Compose override to add this service
└── .env.example
```

---

## Planned future features (ideas)

- **Sentiment scoring** on news articles (add a `/ai/news/sentiment` endpoint)
- **Risk alerts** — proactive push when a position drops X% in a day
- **Client report generation** — PDF-ready summaries via the `/ai/portfolio/report` endpoint
- **Streaming chat** — switch to SSE for real-time token streaming in the frontend
