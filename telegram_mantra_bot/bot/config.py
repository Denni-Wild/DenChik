import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    bot_token: str
    openai_api_key: str
    db_url: str
    openrouter_api_key: str
    gpt_prefix: str
    gpt_suffix: str

def load_config() -> Config:
    return Config(
        bot_token=os.getenv('BOT_TOKEN', ''),
        openai_api_key=os.getenv('OPENAI_API_KEY', ''),
        db_url=os.getenv('DATABASE_URL', ''),
        openrouter_api_key=os.getenv('OPENROUTER_API_KEY', ''),
        gpt_prefix="""Ты — эксперт по созданию персональных мантр. На основе ответов пользователя создай мощную, 
        глубокую и персонализированную мантру. Мантра должна быть:
        - Краткой (1-2 предложения)
        - Позитивной
        - Личной (используй местоимение "я")
        - Написанной в настоящем времени
        - Эмоционально резонирующей
        
        Вот ответы пользователя на сократические вопросы:
        """,
        gpt_suffix="""

        Создай мантру, которая поможет пользователю трансформировать его состояние и укрепить позитивные изменения.
        Ответь ТОЛЬКО текстом мантры, без дополнительных пояснений."""
    )

# оставим эти константы для обратной совместимости (если где-то используются)
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
