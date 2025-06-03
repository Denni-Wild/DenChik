from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# --- Главное меню ---
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Мои мантры"), KeyboardButton(text="➕ Новая мантра")],
            [KeyboardButton(text="💳 Подписка / Оплата")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        persistent=True
    )

# --- Внутри раздела мои мантры ---
def my_mantras_keyboard(mantras_list=None):
    """
    Создает клавиатуру со списком мантр пользователя
    mantras_list: список кортежей (id, текст_мантры)
    """
    if not mantras_list:
        mantras_list = []
    
    keyboard = []
    for mantra_id, mantra_text in mantras_list:
        # Обрезаем текст мантры для кнопки
        short_text = mantra_text[:30] + "..." if len(mantra_text) > 30 else mantra_text
        keyboard.append([InlineKeyboardButton(
            text=f"🧘 {short_text}",
            callback_data=f"mantra_{mantra_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="➕ Новая мантра", callback_data="start_new_mantra")])
    keyboard.append([InlineKeyboardButton(text="◀️ Главное меню", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- Внутри мантры ---
def mantra_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Текст", callback_data="show_text")],
        [
            InlineKeyboardButton(text="🎧 Моя запись", callback_data="play_recording"),
            InlineKeyboardButton(text="🔁 Перезаписать", callback_data="record_mantra")
        ],
        [
            InlineKeyboardButton(text="✏️ Доработать", callback_data="edit_mantra"),
            InlineKeyboardButton(text="📢 Заказать начитку", callback_data="order_voiceover")
        ],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_mantra")],
        [InlineKeyboardButton(text="◀️ Назад к мантрам", callback_data="back_to_mantras")]
    ])

# --- Стартовый диалог для создания мантры ---
def start_request_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Да, у меня есть запрос", callback_data="has_request")],
        [InlineKeyboardButton(text="🔎 Хочу сначала разобраться, что у меня внутри", callback_data="explore_inside")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_mantras")]
    ])

def request_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Написать текстом", callback_data="request_text")],
        [InlineKeyboardButton(text="💬 Подключить голосовую отправку (подписка)", callback_data="enable_voice")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_request_start")]
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
            InlineKeyboardButton(text="📝 Получить новую мантру", callback_data="start_new_mantra"),
            InlineKeyboardButton(text="💫 Поделиться", callback_data="share_mantra")
        ],
        [InlineKeyboardButton(text="❤️ Сохранить", callback_data="favorite_mantra")],
        [InlineKeyboardButton(text="◀️ Назад к мантрам", callback_data="back_to_mantras")]
    ])
    return keyboard

