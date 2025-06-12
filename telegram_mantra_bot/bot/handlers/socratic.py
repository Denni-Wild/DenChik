from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..config import load_config
import openai
import asyncio
from ..ai_utils import generate_socratic_questions_openrouter, generate_next_socratic_question_openrouter
import logging, tempfile, os, subprocess, speech_recognition as sr
from ..sheets import get_message, save_response, save_questions_block, save_ai_result

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

router = Router()

# FSM-состояния прямо здесь
class SocraticFSM(StatesGroup):
    waiting_for_answer = State()
    done = State()

# --- Запрос к OpenRouter через openai (sync-wrapper для asyncio) ---
async def generate_socratic_questions_openrouter(block, description, openrouter_api_key, num_questions=6):
    config = load_config()
    openai.api_key = openrouter_api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    model_name = "mistralai/mixtral-8x7b-instruct"  # Или любую поддерживаемую модель

    prompt = config.socratic_prompt.format(
        num_questions=num_questions,
        block=block,
        description=description
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
    return [q for q in questions if q][:num_questions]

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

    # Получаем приветственное сообщение из Google Sheets
    intro_message = get_message(f"socratic_intro_{block.lower()}") or "Формирую персональные вопросы для тебя…"
    await query.message.answer(intro_message)

    config = load_config()
    questions = await generate_socratic_questions_openrouter(
        block, description, config.openrouter_api_key, config.socratic_questions_count
    )

    # Сохраняем выбранное чувство в state
    await state.update_data(socratic_questions=questions, socratic_answers=[], current_idx=0, feelings=description)
    
    # Получаем текст первого вопроса из Google Sheets или используем сгенерированный
    first_question = get_message(f"socratic_q1_{block.lower()}") or questions[0]
    await query.message.answer(f"Вопрос 1 из {len(questions)}:\n{first_question}")
    await state.set_state(SocraticFSM.waiting_for_answer)

@router.message(SocraticFSM.waiting_for_answer, F.voice)
async def handle_voice_socratic_answer(message: types.Message, state: FSMContext):
    logger.info(f'[FSM] Получено голосовое сообщение (диагностика) от пользователя {message.from_user.id}')
    
    # Скачиваем голосовое сообщение
    file = await message.bot.get_file(message.voice.file_id)
    file_path = file.file_path
    
    # Создаём временный файл для сохранения
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_ogg:
        await message.bot.download_file(file_path, temp_ogg)
        temp_ogg_path = temp_ogg.name

    # Конвертируем в WAV для распознавания
    wav_path = temp_ogg_path + '.wav'
    try:
        subprocess.run(['ffmpeg', '-i', temp_ogg_path, wav_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'[FSM] Ошибка конвертации аудио: {e}')
        await message.answer('Произошла ошибка при обработке аудио.')
        return

    # Распознаём речь
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            logger.info(f'[FSM] Расшифрованный текст голосового ответа пользователя {message.from_user.id}: {text}')
            await message.answer(f'Ваше сообщение:\n[ {text} ]')
            
            # Добавляем ответ в state и двигаемся дальше как с текстом
            data = await state.get_data()
            questions = data.get('socratic_questions', [])
            answers = data.get('socratic_answers', [])
            idx = data.get('current_idx', 0)
            
            # Сохраняем ответ в Google Sheets (Responses)
            save_response(message.from_user.id, f"socratic_q{idx+1}", text)
            # Добавляем ответ в state
            answers.append(text)
            idx += 1
            config = load_config()
            max_questions = config.socratic_questions_count
            if idx < max_questions:
                await state.update_data(socratic_answers=answers, current_idx=idx)
                data = await state.get_data()
                user_request = data.get('user_request', data.get('feelings', ''))
                history = list(zip(data.get('socratic_questions', []), data.get('socratic_answers', [])))
                # Получаем следующий вопрос через ИИ
                next_question = await generate_next_socratic_question_openrouter(
                    user_request=user_request,
                    history=history,
                    openrouter_api_key=config.openrouter_api_key
                )
                questions = data.get('socratic_questions', []) + [next_question]
                await state.update_data(socratic_questions=questions)
                await message.answer(f"Вопрос {idx+1} из {max_questions}:\n{next_question}")
                await state.set_state(SocraticFSM.waiting_for_answer)
            else:
                await state.update_data(socratic_answers=answers)
                # Сохраняем все вопросы и ответы в одну колонку
                data = await state.get_data()
                q_and_a = list(zip(data.get('socratic_questions', []), data.get('socratic_answers', [])))
                user_request = data.get('user_request')
                if user_request:
                    q_and_a = [("Ваш запрос", user_request)] + q_and_a
                save_questions_block(message.from_user.id, q_and_a)
                completion_msg = get_message("socratic_completion") or "Спасибо за ваши искренние ответы! Теперь я смогу подготовить для вас персональную мантру ✨"
                await message.answer(completion_msg)
                await state.set_state(SocraticFSM.done)
                from .gpt import generate_mantra
                await generate_mantra(message, {"feelings": data.get("feelings", ""), "socratic_answers": data.get("socratic_answers", [])})
        except sr.UnknownValueError:
            await message.answer('Не удалось распознать речь.')
        except sr.RequestError as e:
            await message.answer('Ошибка сервиса распознавания речи.')
        finally:
            try:
                source.close()
            except Exception:
                pass
            # Удаляем временные файлы
            for path in [temp_ogg_path, wav_path]:
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f'[FSM] Ошибка при удалении временных файлов: {e}')

@router.message(SocraticFSM.waiting_for_answer)
async def receive_socratic_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get('socratic_questions', [])
    answers = data.get('socratic_answers', [])
    idx = data.get('current_idx', 0)
    config = load_config()
    max_questions = config.socratic_questions_count
    # Сохраняем ответ в Responses
    save_response(message.from_user.id, f"socratic_q{idx+1}", message.text)
    answers.append(message.text)
    idx += 1
    if idx < max_questions:
        await state.update_data(socratic_answers=answers, current_idx=idx)
        user_request = data.get('user_request', data.get('feelings', ''))
        history = list(zip(data.get('socratic_questions', []), data.get('socratic_answers', [])))
        # Получаем следующий вопрос через ИИ
        next_question = await generate_next_socratic_question_openrouter(
            user_request=user_request,
            history=history,
            openrouter_api_key=config.openrouter_api_key
        )
        questions = data.get('socratic_questions', []) + [next_question]
        await state.update_data(socratic_questions=questions)
        await message.answer(f"Вопрос {idx+1} из {max_questions}:\n{next_question}")
        await state.set_state(SocraticFSM.waiting_for_answer)
    else:
        await state.update_data(socratic_answers=answers)
        # Сохраняем все вопросы и ответы в одну колонку
        data = await state.get_data()
        q_and_a = list(zip(data.get('socratic_questions', []), data.get('socratic_answers', [])))
        user_request = data.get('user_request')
        if user_request:
            q_and_a = [("Ваш запрос", user_request)] + q_and_a
        save_questions_block(message.from_user.id, q_and_a)
        completion_msg = get_message("socratic_completion") or "Спасибо за ваши искренние ответы! Теперь я смогу подготовить для вас персональную мантру ✨"
        await message.answer(completion_msg)
        await state.set_state(SocraticFSM.done)
        from .gpt import generate_mantra
        await generate_mantra(message, {"feelings": data.get("feelings", ""), "socratic_answers": data.get("socratic_answers", [])})
