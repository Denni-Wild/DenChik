# bot/handlers/reminders.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from ..keyboards import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)
router = Router()

class ReminderStates(StatesGroup):
    waiting_for_time = State()


def schedule_reminder(db, user_id: int, mantra_id: int, remind_at):
    """
    Создать запись напоминания в базе данных.
    """
    reminder = Reminder(
        user_id=user_id,
        mantra_id=mantra_id,
        remind_at=remind_at,
        sent=False
    )
    db.add(reminder)
    db.commit()


@router.callback_query(F.data == "next_step")
async def on_next_step(query: types.CallbackQuery):
    """
    Обработка нажатия «✅ Продолжить»
    """
    # Здесь ваша логика перехода к следующей мантре
    await query.answer("Переходим к следующей мантре…")
    # Например, вызвать функцию генерации нового вопроса или отправить следующий шаг


@router.callback_query(F.data == "skip_step")
async def on_skip_step(query: types.CallbackQuery):
    """
    Обработка нажатия «🔄 Пропустить»
    """
    await query.answer("Шаг пропущен.")
    # Дополнительная логика при пропуске шага


@router.callback_query(F.data == "roadmap")
async def on_roadmap(query: types.CallbackQuery):
    """
    Обработка нажатия «❓ Маршрут»
    """
    # Получите маршрут из базы данных и отправьте пользователю
    await query.message.answer("Вот ваш текущий маршрут:", reply_markup=continue_keyboard())
    await query.answer()


@router.callback_query(F.data == "back_to_main")
async def return_to_main(callback: types.CallbackQuery):
    """Вернуться в главное меню"""
    logger.info("Пользователь возвращается в главное меню")
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=main_menu_keyboard()
    )
    await callback.message.delete()
