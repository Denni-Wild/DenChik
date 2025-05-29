# bot/handlers/gpt.py

from aiogram import Router, types, F
from datetime import datetime, timedelta
from ..config import load_config
from ..models import SessionLocal, Mantra, Reminder, Topic, Answer
from .reminders import schedule_reminder
import openai

router = Router()


@router.callback_query(F.data == "generate_mantra")
async def generate_mantra_handler(query: types.CallbackQuery, state: dict):
    """
    Генерация мантры через GPT-4 и планирование напоминания
    """
    # Загружаем конфиг и ключ
    config = load_config()
    openai.api_key = config.openai_api_key

    # Получаем из state ID темы и ответы
    topic_id = state.get("topic_id")
    if topic_id is None:
        await query.answer("Не удалось найти тему для генерации мантры.", show_alert=True)
        return

    db = SessionLocal()
    topic = db.query(Topic).get(topic_id)

    # Собираем ответы по порядку
    answers = (
        db.query(Answer)
          .filter_by(topic_id=topic.id)
          .order_by(Answer.question_index)
          .all()
    )
    prompt = (
        config.gpt_prefix
        + "\n".join(a.answer_text for a in answers)
        + config.gpt_suffix
    )

    # Запрос к OpenAI GPT-4
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    mantra_text = resp.choices[0].message.content.strip()

    # Сохраняем мантру и обновляем шаг
    mantra = Mantra(
        topic_id=topic.id,
        text=mantra_text,
        step_index=topic.current_step
    )
    db.add(mantra)
    topic.current_step += 1
    db.commit()
    db.refresh(mantra)

    # Планируем напоминание через 24 часа
    remind_at = datetime.utcnow() + timedelta(hours=24)
    schedule_reminder(db, query.from_user.id, mantra.id, remind_at)
    db.close()

    # Отправляем пользователю текст мантры
    await query.message.answer(
        mantra_text,
        reply_markup=None  # или добавьте continue_keyboard(), если нужно
    )
    await query.answer()
