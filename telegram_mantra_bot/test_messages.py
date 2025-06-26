#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы загрузки сообщений
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

# Импортируем модули бота
from bot.sheets import init_sheets_client
from bot.messages import debug_messages, get_message, reload_messages

def main():
    print("🧪 Тестирование системы загрузки сообщений")
    print("=" * 50)
    
    # Инициализируем Google Sheets клиент
    print("\n1. Инициализация Google Sheets...")
    sheets_ok = init_sheets_client()
    if sheets_ok:
        print("✅ Google Sheets клиент инициализирован")
    else:
        print("⚠️ Google Sheets клиент не инициализирован (будем использовать .env и дефолты)")
    
    # Запускаем отладку
    print("\n2. Отладочная информация:")
    debug_messages()
    
    # Тестируем конкретные сообщения
    print("\n3. Тестирование конкретных сообщений:")
    test_keys = [
        "welcome_message",
        "help_message", 
        "socratic_intro",
        "completion_message",
        "nonexistent_key"
    ]
    
    for key in test_keys:
        value = get_message(key)
        print(f"  {key}: {value}")
    
    # Тестируем перезагрузку
    print("\n4. Тестирование перезагрузки кэша:")
    reload_messages()
    print("✅ Кэш перезагружен")
    
    print("\n🎯 Тестирование завершено!")

if __name__ == "__main__":
    main() 