from aiogram import Router, types
from aiogram.filters import Command
from ..keyboards import main_menu_keyboard
from ..models import get_or_create_user, SessionLocal
from ..sheets import add_or_update_user
from ..messages import get_message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    """
    db = SessionLocal()
    get_or_create_user(message.from_user.id, message.from_user.username)
    db.close()

    # Добавляем или обновляем пользователя в Google Sheets
    user = message.from_user
    add_or_update_user({
        'user_id': user.id,
        'username': user.username or '',
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
    })

    text = get_message("welcome_message")
    await message.answer(text, reply_markup=main_menu_keyboard())
