from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..keyboards import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "back_to_main")
async def return_to_main(callback: types.CallbackQuery):
    """Вернуться в главное меню"""
    logger.info("Пользователь возвращается в главное меню")
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=main_menu_keyboard()
    )
    await callback.message.delete() 