import json
from app.models.schemas import ClientContext, StockQuote
from app.services.ia_client import complete

SYSTEM = """You are a financial assistant embedded in Findash, a portfolio management dashboard.
You give concise, actionable insights to financial advisors. Always:
- Use the client's risk profile (conservative / moderate / aggressive) to calibrate tone.
- Cite specific numbers from the portfolio data provided.
- Be direct. Advisors are busy. Bullet points are fine.
- Never give generic advice. If data is insufficient, say so and ask for what's missing.
- Do NOT invent prices or performance numbers.
"""


def analyze_portfolio(client: ClientContext, quotes: list[StockQuote]) -> str:
    """
    Given a client's portfolio + live quotes, return an AI-generated analysis.
    The Node backend fetches quotes and sends them here — no Yahoo Finance calls from Python.
    """
    quote_map = {q.symbol: q for q in quotes}

    # Build enriched positions with current P&L
    enriched = []
    total_cost = 0.0
    total_value = 0.0
    for pos in client.portfolio:
        q = quote_map.get(pos.symbol)
        cost = pos.quantity * pos.avgBuyPrice
        value = pos.quantity * q.price if q else None
        pnl = value - cost if value is not None else None
        pnl_pct = (pnl / cost * 100) if pnl is not None and cost else None
        total_cost += cost
        total_value += value or cost
        enriched.append({
            "symbol": pos.symbol,
            "name": pos.name,
            "quantity": pos.quantity,
            "avgBuyPrice": pos.avgBuyPrice,
            "currentPrice": q.price if q else "unavailable",
            "unrealizedPnL": round(pnl, 2) if pnl is not None else "unavailable",
            "unrealizedPnL_pct": round(pnl_pct, 2) if pnl_pct is not None else "unavailable",
            "changePercent_today": round(q.changePercent, 2) if q else "unavailable",
        })

    portfolio_summary = {
        "client": client.name,
        "riskProfile": client.riskProfile,
        "totalCost": round(total_cost, 2),
        "totalCurrentValue": round(total_value, 2),
        "totalUnrealizedPnL": round(total_value - total_cost, 2),
        "positions": enriched,
    }

    prompt = f"""Analyze this client portfolio and provide:
1. Overall performance summary (2-3 sentences)
2. Top opportunities / risks based on today's movements
3. One concrete suggestion aligned with the client's risk profile

Portfolio data:
{json.dumps(portfolio_summary, indent=2)}
"""
    return complete(SYSTEM, [{"role": "user", "content": prompt}])


def suggest_rebalance(client: ClientContext, quotes: list[StockQuote]) -> str:
    """Return a rebalancing suggestion based on risk profile and current weights."""
    quote_map = {q.symbol: q for q in quotes}
    total_value = sum(
        pos.quantity * (quote_map[pos.symbol].price if pos.symbol in quote_map else pos.avgBuyPrice)
        for pos in client.portfolio
    )
    weights = []
    for pos in client.portfolio:
        price = quote_map[pos.symbol].price if pos.symbol in quote_map else pos.avgBuyPrice
        value = pos.quantity * price
        weights.append({"symbol": pos.symbol, "weight_pct": round(value / total_value * 100, 1) if total_value else 0})

    prompt = f"""Client: {client.name} | Risk profile: {client.riskProfile}
Current portfolio weights:
{json.dumps(weights, indent=2)}

Suggest a rebalancing plan. Be specific about which positions to reduce/increase and by roughly how much.
Keep it under 150 words.
"""
    return complete(SYSTEM, [{"role": "user", "content": prompt}])
