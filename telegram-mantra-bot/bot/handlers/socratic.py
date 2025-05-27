# bot/handlers/socratic.py
from aiogram import Router, types, F
from aiogram.types import CallbackQuery

from ..models import SessionLocal, User, Topic, Answer
from ..keyboards import socratic_keyboard

router = Router()

@router.callback_query(F.data == "start_diagnostics")
async def start_diagnostics(query: types.CallbackQuery, state: dict):
    """
    Запуск сократической сессии — создаём тему и задаём первый вопрос
    """
    db = SessionLocal()
    user_id = query.from_user.id
    # Создаём новую тему «Диагностика»
    topic = Topic(user_id=await User.id_by_telegram(db, user_id), title="Диагностика")
    db.add(topic)
    db.commit()
    db.refresh(topic)
    db.close()

    # Сохраняем ID темы и список вопросов в state
    state['topic_id'] = topic.id
    questions = [
        "Что ты чаще всего ощущаешь в последнее время — внутри себя, в фоне?",
        "Когда и где ты впервые заметил(а) это состояние?",
        "Что обычно запускает это чувство?",
        "Как оно влияет на твои решения и действия?",
        "Чего ты хочешь достичь, прорабатывая это состояние?",
    ]
    state['questions'] = questions
    state['question_idx'] = 0

    # Отправляем первый вопрос с кнопками
    await query.message.edit_text(
        questions[0],
        reply_markup=socratic_keyboard(question_index=0, total=len(questions))
    )
    await query.answer()


@router.callback_query(F.data.startswith("answer_"))
async def handle_answer(query: types.CallbackQuery, state: dict):
    """
    Принимаем ответ на вопрос и либо переходим к следующему, либо запускаем генерацию мантры
    """
    # Разбираем индекс и текст из callback_data вида "answer_0:Мой ответ"
    idx_str, text = query.data.split(":", 1)
    idx = int(idx_str.split("_")[1])

    # Сохраняем ответ в БД
    db = SessionLocal()
    answer = Answer(
        topic_id=state['topic_id'],
        question_index=idx,
        answer_text=text
    )
    db.add(answer)
    db.commit()
    db.close()

    questions = state['questions']
    next_idx = idx + 1

    if next_idx < len(questions):
        # Переходим к следующему вопросу
        await query.message.edit_text(
            questions[next_idx],
            reply_markup=socratic_keyboard(question_index=next_idx, total=len(questions))
        )
    else:
        # Все ответы получены — просим генерацию мантры
        await query.message.edit_text(
            "Спасибо за ответы! Теперь нажмите кнопку ниже, чтобы сгенерировать вашу персональную мантру.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🪄 Сгенерировать мантру", callback_data="generate_mantra")]
            ])
        )

    await query.answer()
