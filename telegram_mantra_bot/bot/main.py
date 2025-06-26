# bot/main.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.client.default import DefaultBotProperties
from telegram_mantra_bot.bot.config import load_config
from telegram_mantra_bot.bot.sheets import init_sheets_client
from telegram_mantra_bot.bot.messages import load_all_messages
from aiogram import types

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(
            command="start",
            description="Запустить бота"
        ),
        BotCommand(
            command="help",
            description="Показать справку"
        )
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

async def main():
    """Основная функция запуска бота"""
    # Загружаем конфигурацию
    config = load_config()
    
    # Инициализируем Google Sheets клиент
    logger.info("Инициализация Google Sheets клиента...")
    if not init_sheets_client():
        logger.error("Не удалось инициализировать Google Sheets клиент!")
        return
    
    # Загружаем сообщения из Google Sheets
    logger.info("Загрузка сообщений из Google Sheets...")
    load_all_messages()
    
    # Инициализируем бота и диспетчер
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Импортируем и регистрируем роутеры только после полной инициализации
    from telegram_mantra_bot.bot.handlers.start import router as start_router
    from telegram_mantra_bot.bot.handlers.socratic import router as socratic_router
    from telegram_mantra_bot.bot.handlers.mantra_actions import router as mantra_actions_router
    from telegram_mantra_bot.bot.handlers.gpt import router as gpt_router
    from telegram_mantra_bot.bot.handlers.voice import router as voice_router
    
    # Глобальный fallback-хендлер
    async def fallback_handler(update: types.Update):
        user_id = None
        if update.message:
            user_id = update.message.from_user.id
            content = str(update.message)
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
            content = str(update.callback_query)
        else:
            content = str(update)
        logger.warning(f"[FALLBACK] Необработанный апдейт: type={update.event_type}, user_id={user_id}, content={content[:200]}")

    # Регистрируем роутеры
    dp.include_router(start_router)
    dp.include_router(socratic_router)
    dp.include_router(mantra_actions_router)
    dp.include_router(gpt_router)
    dp.include_router(voice_router)
    dp.message.outer_middleware(lambda handler, event, data: fallback_handler(event.update) if handler is None else handler(event, data))
    
    # Устанавливаем команды бота
    await set_commands(bot)
    
    # Запускаем поллинг
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
