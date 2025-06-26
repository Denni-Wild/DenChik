#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)
# Добавляем загрузку .env
from dotenv import load_dotenv
load_dotenv()

def main():
    print("🔍 Детальная отладка Google Sheets")
    print("=" * 50)
    
    # 1. Проверяем переменные окружения
    print("\n1. Проверка переменных окружения:")
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    print(f"  GOOGLE_SHEETS_ID: {sheets_id or 'НЕ УСТАНОВЛЕНА'}")
    
    # 2. Проверяем файл cred2.json
    print("\n2. Проверка файла cred2.json:")
    cred_file = "cred2.json"
    if os.path.exists(cred_file):
        print(f"  ✅ Файл {cred_file} найден")
        try:
            import json
            with open(cred_file, 'r') as f:
                cred_data = json.load(f)
            print(f"  📄 Тип аккаунта: {cred_data.get('type', 'неизвестно')}")
            print(f"  📧 Email: {cred_data.get('client_email', 'неизвестно')}")
        except Exception as e:
            print(f"  ❌ Ошибка чтения файла: {e}")
    else:
        print(f"  ❌ Файл {cred_file} НЕ НАЙДЕН")
    
    # 3. Пробуем инициализировать Google Sheets
    print("\n3. Попытка инициализации Google Sheets:")
    try:
        from telegram_mantra_bot.bot.sheets import init_sheets_client
        sheets_ok = init_sheets_client()
        # Переимпортируем sheets_client после инициализации
        from telegram_mantra_bot.bot.sheets import sheets_client
        print(f"  sheets_client после init: {sheets_client}")
        if sheets_ok and sheets_client:
            print("  ✅ Google Sheets клиент инициализирован")
            
            # 4. Пробуем получить сообщения
            print("\n4. Попытка получения сообщений:")
            if sheets_client:
                messages = sheets_client.get_all_messages()
                print(f"  📊 Получено сообщений: {len(messages)}")
                if messages:
                    print("  📝 Ключи сообщений:")
                    for key in list(messages.keys())[:5]:  # Показываем первые 5
                        print(f"    - {key}: {messages[key][:50]}...")
                else:
                    print("  ⚠️ Сообщений не найдено")
                    
                    # Проверяем, что именно ищет система
                    print("\n5. Проверка диапазона поиска:")
                    print(f"  📋 SPREADSHEET_ID: {sheets_id}")
                    print(f"  📋 MESSAGES_RANGE: keys!A2:C")
                    print("  📋 Ожидаемая структура:")
                    print("     A (Name) | B (value) | C (description)")
                    print("     welcome_message | Привет! | Приветственное сообщение")
                    
            else:
                print("  ❌ sheets_client не инициализирован")
        else:
            print("  ❌ Не удалось инициализировать Google Sheets клиент")
            
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Отладка завершена!")

if __name__ == "__main__":
    main() 