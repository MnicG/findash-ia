from openai import OpenAI
from app.core.config import settings

_client: OpenAI | None = None

# Model to use from Chutes — swap this string to change models
CHUTES_MODEL = "google/gemma-3-27b-it"  # Gemma 4 31B Turbo on Chutes


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.CHUTES_API_KEY,
            base_url="https://llm.chutes.ai/v1",  # Chutes OpenAI-compatible endpoint
        )
    return _client


def complete(system: str, messages: list[dict], max_tokens: int = 1024) -> str:
    """Simple single-turn or multi-turn completion via Chutes."""
    all_messages = [{"role": "system", "content": system}] + messages

    response = get_client().chat.completions.create(
        model="google/gemma-4-31B-turbo-TEE",
        max_tokens=max_tokens,
        messages=all_messages,
    )
    return response.choices[0].message.content
