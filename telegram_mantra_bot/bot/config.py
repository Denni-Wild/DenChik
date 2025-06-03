import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    bot_token: str
    openrouter_api_key: str
    openai_api_key: str
    ai_model: str
    database_url: str

def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        ai_model=os.getenv("AI_MODEL", "mistralai/mixtral-8x7b-instruct"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///bot.db")
    )

# оставим эти константы для обратной совместимости (если где-то используются)
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
