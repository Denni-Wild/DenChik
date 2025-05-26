# bot/handlers/start.py

from aiogram import Router, types
from aiogram.filters import Command
from ..keyboards import start_keyboard
from ..models import get_or_create_user, SessionLocal

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Приветствие и главное меню
    """
    db = SessionLocal()
    # Создать или получить пользователя по telegram_id
    get_or_create_user(db, message.from_user.id, message.from_user.username)
    db.close()

    text = (
        "Привет!\n"
        "Этот бот помогает найти внутреннюю опору, создать персональную мантру "
        "и понять, что с вами происходит — мягко, бережно и по-настоящему индивидуально.\n"
        "У вас уже есть какой-то внутренний запрос или чувство, с которым хотите поработать?"
    )
    await message.answer(text, reply_markup=start_keyboard())
