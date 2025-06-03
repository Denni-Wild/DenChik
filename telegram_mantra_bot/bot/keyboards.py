from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Приветствие и стартовое меню ---
def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Да, у меня есть запрос", callback_data="has_request")],
        [InlineKeyboardButton(text="🔎 Хочу сначала разобраться, что у меня внутри", callback_data="explore_inside")]
    ])

def request_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Написать текстом", callback_data="request_text")],
        [InlineKeyboardButton(text="💬 Подключить голосовую отправку (подписка)", callback_data="enable_voice")]
    ])

def voice_subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="has_request")]
    ])

def start_diag_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧭 Пройти самодиагностику", callback_data="start_diagnostics")]
    ])

# --- Клавиатуры для диагностики ---
def diagnostics_state_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="😟 Негативное", callback_data="diag_negative"),
            InlineKeyboardButton(text="😐 Нейтральное", callback_data="diag_neutral"),
            InlineKeyboardButton(text="🧘 Позитивное", callback_data="diag_positive"),
        ]
    ])

def detailed_state_keyboard(states):
    # states — список кортежей (текст кнопки, callback_data)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=cb)] for text, cb in states
    ])

# --- Клавиатуры для напоминаний и маршрутов ---
def continue_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить", callback_data="next_step")],
        [InlineKeyboardButton(text="🔄 Пропустить", callback_data="skip_step")],
        [InlineKeyboardButton(text="❓ Маршрут", callback_data="roadmap")]
    ])

def roadmap_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Посмотреть маршрут", callback_data="show_roadmap")]
    ])
def socratic_keyboard(question_index: int = 0, total: int = 5):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Ответить ({question_index + 1}/{total})",
                    callback_data=f"socratic_answer_{question_index}"
                )
            ]
        ]
    )

def get_mantra_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура после получения мантры
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎙 Записать мантру голосом", callback_data="record_mantra"),
            InlineKeyboardButton(text="🎧 Заказать начитку", callback_data="order_voiceover")
        ],
        [
            InlineKeyboardButton(text="📝 Получить новую мантру", callback_data="new_mantra"),
            InlineKeyboardButton(text="💫 Поделиться", callback_data="share_mantra")
        ],
        [
            InlineKeyboardButton(text="❤️ Сохранить в избранное", callback_data="favorite_mantra")
        ]
    ])
    return keyboard

