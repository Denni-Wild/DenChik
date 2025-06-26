import os
from dotenv import load_dotenv
from .sheets import init_sheets_client, get_message as get_gsheet_message
import logging

# Настраиваем логгер
logger = logging.getLogger(__name__)

# Кэш для всех сообщений
_messages_cache = {}  # Инициализируем как пустой словарь вместо None

def load_all_messages():
    """Загружает все сообщения из Google Sheets в кэш"""
    global _messages_cache  # Явно указываем, что будем изменять глобальную переменную
    try:
        # Получаем все сообщения из таблицы через get_gsheet_message
        messages = {}
        # Список всех ключей, которые мы хотим загрузить
        keys_to_load = [
            "welcome_message",
            "help_message",
            "socratic_intro",
            "socratic_initial_question",
            "completion_message",
            "final_message",
            "socratic_error_voice",
            "socratic_error_processing",
            "socratic_voice_recognized",
            "socratic_help",
            "socratic_timeout"
        ]
        
        for key in keys_to_load:
            value = get_gsheet_message(key)
            if value:
                messages[key] = value
        
        if not messages:
            logger.warning("Не удалось получить сообщения из таблицы")
            return

        # Очищаем кэш перед загрузкой новых данных
        _messages_cache.clear()
        
        # Загружаем сообщения в кэш
        for key, value in messages.items():
            _messages_cache[key] = value
        
        # Логируем все загруженные переменные одним компактным сообщением
        summary = f"Загружено {len(_messages_cache)} переменных: " + ", ".join([
            f"{k}='{(v[:50] + '...' if len(v) > 50 else v)}'" for k, v in _messages_cache.items()
        ])
        logger.info(summary)

    except Exception as e:
        logger.error(f"Ошибка при загрузке сообщений: {e}")

def get_message(key: str, default: str = None) -> str:
    """Получает сообщение из кэша, переменных окружения или возвращает значение по умолчанию"""
    global _messages_cache
    
    # Если кэш пустой, пробуем загрузить сообщения
    if not _messages_cache:
        load_all_messages()
    
    # Сначала проверяем кэш
    if key in _messages_cache:
        return _messages_cache[key]
    
    # Затем проверяем переменные окружения
    env_key = f"MESSAGE_{key.upper()}"
    if env_value := os.getenv(env_key):
        logger.info(f"Переменная {key} загружена из окружения")
        return env_value
    
    # Если значение не найдено, логируем это
    if default is None:
        logger.warning(f"Переменная {key} не найдена ни в таблице, ни в окружении")
    else:
        logger.info(f"Переменная {key} не найдена, используется значение по умолчанию")
    
    return default

def debug_messages():
    """Функция для отладки - показывает откуда загружаются сообщения"""
    print("\n[DEBUG] Система загрузки сообщений:")
    print("1. Google Sheets (приоритет 1)")
    print("2. .env файл (приоритет 2)") 
    print("3. Дефолтные значения (приоритет 3)")
    
    print("\n[DEBUG] Ключи дефолтных сообщений:")
    defaults = {
        "welcome_message": "Привет! Я бот, который поможет тебе с мантрами и саморефлексией.",
        "help_message": "Вот как пользоваться ботом...",
        "socratic_intro": "Сейчас я задам тебе несколько вопросов...",
        "completion_message": "Спасибо за ответы! Я подготовлю для тебя персональную мантру.",
    }
    for k in defaults.keys():
        print(f"  - {k}")
    
    # Загружаем сообщения если еще не загружены
    if _messages_cache is None:
        load_all_messages()
    
    if _messages_cache:
        print("\n[DEBUG] Ключи сообщений из Google Sheets:")
        for k in _messages_cache.keys():
            print(f"  - {k}")
    else:
        print("\n[DEBUG] Сообщения из Google Sheets не загружены или пусты.")
        
    
    print("\n[DEBUG] Примеры загрузки сообщений:")
    test_keys = ["welcome_message", "help_message", "socratic_intro"]
    for key in test_keys:
        value = get_message(key)
        source = "Google Sheets" if _messages_cache and key in _messages_cache else \
                 ".env" if os.getenv(key.upper()) else "дефолт"
        print(f"  {key}: {value[:50]}... (источник: {source})")

# Функция для принудительной перезагрузки кэша
def reload_messages():
    """Принудительно перезагружает сообщения из Google Sheets"""
    global _messages_cache
    _messages_cache = None
    load_all_messages() 