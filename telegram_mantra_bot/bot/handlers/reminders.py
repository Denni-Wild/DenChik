# bot/handlers/reminders.py

from aiogram import Router, types, F
from ..models import SessionLocal, Reminder
from ..keyboards import continue_keyboard

router = Router()


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
