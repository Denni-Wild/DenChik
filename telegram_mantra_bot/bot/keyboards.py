from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Основное меню бота"""
    keyboard = [
        [KeyboardButton(text="Мне нужна помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def my_mantras_keyboard(mantras: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Клавиатура со списком мантр пользователя"""
    keyboard = []
    for mantra in mantras:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗣 {mantra['text'][:30]}...",
                callback_data=f"mantra_{mantra['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_mantra_keyboard(mantra_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра конкретной мантры"""
    keyboard = [
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_mantra_{mantra_id}"),
            InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_mantras")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_delete_keyboard(mantra_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления мантры"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_delete_{mantra_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"mantra_{mantra_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

