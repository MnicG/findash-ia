from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Chutes AI
    CHUTES_API_KEY: str = ""

    # CORS — match your existing frontend origin
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "https://your-frontend.vercel.app"]

    # Internal secret so only your Node backend can call this service
    INTERNAL_API_KEY: str = "change-me-in-production"

    class Config:
        env_file = ".env"


settings = Settings()
