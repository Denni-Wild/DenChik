# bot/main.py

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

import logging
import asyncio

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

try:
    # Try relative imports first (when running as a module)
    from .config import load_config
    from .handlers.start import router as start_router
    from .handlers.mantra_actions import router as mantra_actions_router
    from .handlers.gpt import router as gpt_router
    from .handlers.reminders import router as reminders_router
    from .handlers.selection import router as selection_router
    from .handlers.socratic import router as socratic_router
except ImportError:
    # Fall back to absolute imports (when running as a script)
    from telegram_mantra_bot.bot.config import load_config
    from telegram_mantra_bot.bot.handlers.start import router as start_router
    from telegram_mantra_bot.bot.handlers.mantra_actions import router as mantra_actions_router
    from telegram_mantra_bot.bot.handlers.gpt import router as gpt_router
    from telegram_mantra_bot.bot.handlers.reminders import router as reminders_router
    from telegram_mantra_bot.bot.handlers.selection import router as selection_router
    from telegram_mantra_bot.bot.handlers.socratic import router as socratic_router


async def main():
    # Загрузка конфигурации
    config = load_config()

    # Инициализация бота с HTML-парсингом по умолчанию
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    # Диспетчер для регистрации хендлеров
    dp = Dispatcher()

    try:
        from .models import Base, engine
    except ImportError:
        from telegram_mantra_bot.bot.models import Base, engine

    Base.metadata.create_all(bind=engine)
    
    # Подключаем роутеры из каждого файла-обработчика
    dp.include_router(start_router)
    dp.include_router(mantra_actions_router)
    dp.include_router(gpt_router)
    dp.include_router(reminders_router)
    dp.include_router(selection_router)
    dp.include_router(socratic_router)

    # Опционально: задаём команды бота в меню Telegram
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по командам"),
        BotCommand(command="mantras", description="Мои мантры")
    ])

    # Логирование
    logging.basicConfig(level=logging.INFO)

    # Запуск long polling
    try:
        await dp.start_polling(bot)
    finally:
        # Корректно закрываем HTTP-сессию Aiogram
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
