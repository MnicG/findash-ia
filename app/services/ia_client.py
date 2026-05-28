from openai import OpenAI
from app.core.config import settings
from typing import Iterator

_client: OpenAI | None = None

CHUTES_MODEL = "google/gemma-4-31B-turbo-TEE"


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.CHUTES_API_KEY,
            base_url="https://llm.chutes.ai/v1",
        )
    return _client


def complete(system: str, messages: list[dict], max_tokens: int = 1024) -> str:
    all_messages = [{"role": "system", "content": system}] + messages
    response = get_client().chat.completions.create(
        model=CHUTES_MODEL,
        max_tokens=max_tokens,
        messages=all_messages,
    )
    return response.choices[0].message.content


def complete_stream(system: str, messages: list[dict], max_tokens: int = 1024) -> Iterator[str]:
    """Yields text chunks as they arrive from the model."""
    all_messages = [{"role": "system", "content": system}] + messages
    stream = get_client().chat.completions.create(
        model=CHUTES_MODEL,
        max_tokens=max_tokens,
        messages=all_messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta