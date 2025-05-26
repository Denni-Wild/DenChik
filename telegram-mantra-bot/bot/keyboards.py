# bot/keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Да, у меня есть запрос", callback_data="has_request")],
        [InlineKeyboardButton(text="🔎 Хочу сначала разобраться, что у меня внутри", callback_data="explore_inside")],
    ])

def request_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Написать текстом", callback_data="request_text")],
        [InlineKeyboardButton(text="💬 Подключить голосовую отправку (подписка)", callback_data="enable_voice")],
    ])

def voice_subscription_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оформить голосовую подписку", callback_data="subscribe_voice")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="has_request")],
    ])

def diagnostics_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧭 Пройти самодиагностику", callback_data="start_diagnostics")],
    ])

def socratic_keyboard(question_index: int, total: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для вопросов Сократа:
      - кнопка «Далее» с callback_data вида answer_{index}:{placeholder}
    """
    # Здесь мы просто передаем индекс в callback_data,
    # при обработке вы должны собрать ответ из state или из текста пользователя
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text=f"➡️ Далее ({question_index + 1}/{total})",
            callback_data=f"answer_{question_index}"
        )
    )
    return kb

def continue_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Продолжить", callback_data="next_step"),
            InlineKeyboardButton(text="🔄 Пропустить", callback_data="skip_step"),
        ],
        [InlineKeyboardButton(text="❓ Маршрут", callback_data="roadmap")],
    ])
