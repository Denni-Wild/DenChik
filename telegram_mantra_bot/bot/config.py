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
    socratic_questions_count: int = 6
    google_sheets_id: str = None
    google_credentials_path: str = "google_credentials.json"
    socratic_prompt: str = ""
    mantra_prompt: str = ""

def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        ai_model=os.getenv("AI_MODEL", "mistralai/mixtral-8x7b-instruct"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///bot.db"),
        socratic_questions_count=int(os.getenv("SOCRATIC_QUESTIONS_COUNT", 3)),
        google_sheets_id=os.getenv("GOOGLE_SHEETS_ID"),
        google_credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "google_credentials.json"),
        socratic_prompt=os.getenv("SOCRATIC_PROMPT", "Сформулируй {num_questions} персональных сократических вопросов для пользователя, который выбрал блок '{block}' и описал своё состояние так: '{description}'. Вопросы должны идти по порядку, каждый вопрос с новой строки. Только список вопросов, ничего лишнего."),
        mantra_prompt=os.getenv("MANTRA_PROMPT", "Создай персональную мантру на основе запроса пользователя. Мантра должна быть краткой, позитивной и направленной на трансформацию. Запрос пользователя: {request}")
    )

# оставим эти константы для обратной совместимости (если где-то используются)
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
