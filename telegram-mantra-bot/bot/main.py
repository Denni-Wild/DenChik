# bot/main.py

import logging
import asyncio

from aiogram import Dispatcher
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.types import BotCommand

from .config import load_config
from .handlers.start import router as start_router
from .handlers.selection import router as selection_router
from .handlers.socratic import router as socratic_router
from .handlers.gpt import router as gpt_router
from .handlers.reminders import router as reminders_router


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

    # Подключаем роутеры из каждого файла-обработчика
    dp.include_router(start_router)
    dp.include_router(selection_router)
    dp.include_router(socratic_router)
    dp.include_router(gpt_router)
    dp.include_router(reminders_router)

    # Опционально: задаём команды бота в меню Telegram
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь по командам"),
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
