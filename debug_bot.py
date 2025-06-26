#!/usr/bin/env python3
"""
Проверка токена бота через API Telegram
"""

import asyncio
import logging
from aiogram import Bot
from aiogram.types import BotCommand
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot_token():
    # Загружаем токен из .env
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    
    logger.info(f"Тестируем токен: {token}")
    
    try:
        # Создаем бота
        bot = Bot(token=token)
        
        # Пробуем получить информацию о боте
        bot_info = await bot.get_me()
        logger.info("✅ Токен валидный!")
        logger.info(f"Имя бота: @{bot_info.username}")
        logger.info(f"ID бота: {bot_info.id}")
        logger.info(f"Имя: {bot_info.first_name}")
        
        # Пробуем установить команды
        logger.info("Пробуем установить команды...")
        try:
            await bot.set_my_commands([
                BotCommand(command="test", description="Тестовая команда")
            ])
            logger.info("✅ Команды успешно установлены")
        except Exception as e:
            logger.error(f"❌ Ошибка при установке команд: {e}")
            logger.error(f"Тип ошибки: {type(e)}")
            logger.error(f"Детали ошибки: {str(e)}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке токена: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot_token()) 