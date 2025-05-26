# bot/config.py

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    bot_token: str
    openai_api_key: str
    db_url: str

def load_config() -> Config:
    return Config(
        bot_token=os.getenv('BOT_TOKEN', ''),
        openai_api_key=os.getenv('OPENAI_API_KEY', ''),
        db_url=os.getenv('DATABASE_URL', '')
    )

# добавляем эти константы на уровне модуля
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
