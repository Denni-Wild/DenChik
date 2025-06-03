from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..config import load_config
import openai
import asyncio
from .gpt import generate_mantra

router = Router()

# FSM-состояния прямо здесь
class SocraticFSM(StatesGroup):
    waiting_for_answer = State()
    done = State()

# --- Запрос к OpenRouter через openai (sync-wrapper для asyncio) ---
async def generate_socratic_questions_openrouter(block, description, openrouter_api_key):
    openai.api_key = openrouter_api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    model_name = "mistralai/mixtral-8x7b-instruct"  # Или любую поддерживаемую модель

    prompt = (
        f"Сформулируй 6 персональных сократических вопросов для пользователя, "
        f"который выбрал блок '{block}' и описал своё состояние так: '{description}'. "
        "Вопросы должны идти по порядку, каждый вопрос с новой строки. Только список вопросов, ничего лишнего."
    )

    loop = asyncio.get_running_loop()
    # OpenAI ChatCompletion.create — sync, поэтому через executor:
    response = await loop.run_in_executor(
        None,
        lambda: openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Ты — полезный ассистент, задаёшь вопросы для психологической саморефлексии."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
        )
    )
    questions_text = response["choices"][0]["message"]["content"]
    # Парсим вопросы
    questions = [q.strip("-—. 1234567890) ") for q in questions_text.split('\n') if q.strip()]
    return [q for q in questions if q]

# --- Обработчик старта диалога после выбора блока ---
@router.callback_query(F.data.regexp(r"^block_"))
async def start_socratic_by_block(query: types.CallbackQuery, state: FSMContext):
    block_map = {
        "block_emotion": "ЭМОЦИИ",
        "block_selfesteem": "САМООЦЕНКА",
        "block_behavior": "ПОВЕДЕНИЕ",
        "block_relationship": "ОТНОШЕНИЯ",
        "block_meaning": "СМЫСЛ/МОТИВАЦИЯ",
        "block_emotion2": "ЭМОЦИИ",
        "block_selfesteem2": "САМООЦЕНКА",
        "block_behavior2": "ПОВЕДЕНИЕ",
        "block_behavior3": "ПОВЕДЕНИЕ",
        "block_meaning2": "СМЫСЛ/МОТИВАЦИЯ",
        "block_cbt": "КПТ/ПОВЕДЕНИЕ"
    }
    cb = query.data
    block = block_map.get(cb, cb)
    # Получаем текст выбранной эмоции/состояния с кнопки
    feelings = None
    if hasattr(query.message.reply_markup, 'inline_keyboard'):
        for row in query.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == query.data:
                    feelings = btn.text
                    break
    description = feelings or block

    config = load_config()
    await query.message.answer("Формирую персональные вопросы для тебя…")

    questions = await generate_socratic_questions_openrouter(
        block, description, config.openrouter_api_key
    )

    # Сохраняем выбранное чувство в state
    await state.update_data(socratic_questions=questions, socratic_answers=[], current_idx=0, feelings=description)
    await query.message.answer(f"Вопрос 1 из {len(questions)}:\n{questions[0]}")
    await state.set_state(SocraticFSM.waiting_for_answer)

# FSM: обработка ответов пользователя по вопросам
@router.message(SocraticFSM.waiting_for_answer)
async def receive_socratic_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get('socratic_questions', [])
    answers = data.get('socratic_answers', [])
    idx = data.get('current_idx', 0)

    answers.append(message.text)
    idx += 1

    if idx < len(questions):
        await state.update_data(socratic_answers=answers, current_idx=idx)
        await message.answer(f"Вопрос {idx+1} из {len(questions)}:\n{questions[idx]}")
        await state.set_state(SocraticFSM.waiting_for_answer)
    else:
        await state.update_data(socratic_answers=answers)
        await message.answer("Спасибо за ваши искренние ответы! Теперь я смогу подготовить для вас персональную мантру ✨")
        await state.set_state(SocraticFSM.done)
        # Передаём 'feelings' в generate_mantra
        data = await state.get_data()
        await generate_mantra(message, {"feelings": data.get("feelings", ""), "socratic_answers": data.get("socratic_answers", [])})
