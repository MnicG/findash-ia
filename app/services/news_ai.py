import json
from app.models.schemas import NewsArticle, ClientContext
from app.services.ia_client import complete

SYSTEM = """You are a financial news analyst assistant inside Findash.
Be concise and relevant. Always connect news to portfolio impact when client data is available.
"""


def summarize_news(articles: list[NewsArticle]) -> str:
    """Summarize a list of news articles into key takeaways."""
    article_list = [
        {"title": a.title, "description": a.description, "source": a.source, "publishedAt": a.publishedAt}
        for a in articles
    ]
    prompt = f"""Summarize the following financial news articles into 3-5 key market takeaways.
Use bullet points. Be brief. Focus on what matters for investors today.

Articles:
{json.dumps(article_list, indent=2)}
"""
    return complete(SYSTEM, [{"role": "user", "content": prompt}])


def news_impact_on_portfolio(articles: list[NewsArticle], client: ClientContext) -> str:
    """Explain how today's news may affect a specific client's portfolio."""
    symbols = [pos.symbol for pos in client.portfolio]
    article_list = [
        {"title": a.title, "description": a.description, "source": a.source}
        for a in articles
    ]
    prompt = f"""Client: {client.name} | Risk profile: {client.riskProfile}
Portfolio symbols: {', '.join(symbols)}

Based on today's news below, identify which articles are most relevant to this client's holdings
and briefly explain the potential impact (positive, negative, or neutral).

News:
{json.dumps(article_list, indent=2)}
"""
    return complete(SYSTEM, [{"role": "user", "content": prompt}], max_tokens=800)
