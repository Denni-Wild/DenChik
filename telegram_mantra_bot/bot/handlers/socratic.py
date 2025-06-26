from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ..config import load_config
import openai
import asyncio
from ..ai_utils import generate_next_socratic_question_openrouter
import logging, tempfile, os, subprocess, speech_recognition as sr
from ..sheets import get_message, save_questions_block, save_ai_result
from ..messages import get_message as get_local_message

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

# Список необходимых переменных для сократического диалога
REQUIRED_MESSAGES = {
    # Основные сообщения диалога
    "socratic_intro": "Вступительное сообщение для начала диалога",
    "socratic_initial_question": "Первый вопрос, который задается пользователю",
    "completion_message": "Сообщение при завершении диалога",
    "final_message": "Итоговое сообщение после всех вопросов",
    
    # Сообщения об ошибках и состояниях
    "socratic_error_voice": "Сообщение при ошибке распознавания голоса",
    "socratic_error_processing": "Сообщение при ошибке обработки ответа",
    "socratic_voice_recognized": "Сообщение при успешном распознавании голоса",
    
    # Дополнительные сообщения
    "socratic_help": "Справка по использованию диалога",
    "socratic_timeout": "Сообщение при истечении времени ожидания ответа"
}

# Загружаем и логируем все сообщения из Google Sheets
logger.info("=== Загрузка переменных из Google Sheets ===")
logger.info(f"Попытка загрузить {len(REQUIRED_MESSAGES)} переменных для сократического диалога")

# Словарь для хранения загруженных значений
loaded_messages = {}
missing_messages = []

for msg_key, description in REQUIRED_MESSAGES.items():
    value = get_local_message(msg_key)
    if value:
        loaded_messages[msg_key] = value
        logger.info(f"✓ {msg_key} ({description}):")
        logger.info(f"  Значение: {value[:100]}..." if len(value) > 100 else f"  Значение: {value}")
    else:
        missing_messages.append(msg_key)
        logger.warning(f"✗ {msg_key} ({description}): не найдено в таблице")

# Итоговая статистика
logger.info("=== Итоги загрузки переменных ===")
logger.info(f"Успешно загружено: {len(loaded_messages)} из {len(REQUIRED_MESSAGES)}")
if missing_messages:
    logger.warning("Отсутствующие переменные:")
    for key in missing_messages:
        logger.warning(f"  - {key} ({REQUIRED_MESSAGES[key]})")

router = Router()

# FSM-состояния
class SocraticFSM(StatesGroup):
    waiting_for_answer = State()
    done = State()

async def process_answer(message: types.Message, state: FSMContext, answer_text: str):
    """Обработка ответа пользователя и генерация следующего вопроса"""
    data = await state.get_data()
    dialog_history = data.get('dialog_history', [])
    current_question = data.get('current_question')
    question_count = data.get('question_count', 0)
    config = load_config()
    
    # Добавляем текущий вопрос и ответ в историю
    dialog_history.append((current_question, answer_text))
    
    # Сохраняем всю историю диалога в Google Sheets (дописываем в колонку questions)
    save_questions_block(message.from_user.id, dialog_history)
    
    # Проверяем, достигли ли мы нужного количества вопросов
    if question_count + 1 >= config.socratic_questions_count:
        # Получаем и отправляем сообщение о завершении
        completion_msg = get_local_message("completion_message")
        await message.answer(completion_msg)
        
        # Получаем и отправляем итоговое сообщение
        final_message = get_local_message("final_message")
        if final_message:
            await message.answer(final_message)
        
        # Сохраняем результаты диалога в отдельную колонку
        dialog_summary = "\n".join([f"Вопрос: {q}\nОтвет: {a}\n" for q, a in dialog_history])
        save_ai_result(message.from_user.id, dialog_summary)
        
        await state.set_state(SocraticFSM.done)
        return

    # Генерируем следующий вопрос через ИИ на основе всей истории диалога
    next_question = await generate_next_socratic_question_openrouter(
        user_request=dialog_history[0][1] if dialog_history else "",  # Первый ответ как контекст
        history=dialog_history,
        openrouter_api_key=config.openrouter_api_key
    )
    
    # Обновляем состояние
    await state.update_data(
        dialog_history=dialog_history,
        current_question=next_question,
        question_count=question_count + 1
    )
    
    # Задаем следующий вопрос
    await message.answer(f"Вопрос {question_count + 2}:\n{next_question}")
    await state.set_state(SocraticFSM.waiting_for_answer)

# --- Обработчик старта диалога ---
@router.message(F.text == "Мне нужна помощь")
async def start_socratic_dialog(message: types.Message, state: FSMContext):
    # Получаем вступительное сообщение
    intro_message = get_local_message("socratic_intro")
    await message.answer(intro_message)

    # Получаем начальный вопрос
    initial_question = get_local_message("socratic_initial_question")
    if not initial_question:
        initial_question = "Расскажите, что вас беспокоит?"

    # Сохраняем состояние
    await state.update_data(
        dialog_history=[],
        current_question=initial_question,
        question_count=0
    )
    
    # Задаем первый вопрос
    await message.answer(f"Вопрос 1:\n{initial_question}")
    await state.set_state(SocraticFSM.waiting_for_answer)

@router.message(SocraticFSM.waiting_for_answer, F.voice)
async def handle_voice_socratic_answer(message: types.Message, state: FSMContext):
    """Обработка голосового ответа"""
    logger.info(f'[FSM] Получено голосовое сообщение от пользователя {message.from_user.id}')
    
    # Скачиваем голосовое сообщение
    file = await message.bot.get_file(message.voice.file_id)
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_ogg:
        await message.bot.download(file, destination=temp_ogg)
        temp_ogg_path = temp_ogg.name
    # Конвертируем в WAV для распознавания
    wav_path = temp_ogg_path + '.wav'
    try:
        subprocess.run(['ffmpeg', '-i', temp_ogg_path, wav_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f'[FSM] Ошибка конвертации аудио: {e}')
        error_msg = get_local_message("socratic_error_voice") or "Произошла ошибка при обработке аудио."
        await message.answer(error_msg)
        return
    # Распознаём речь
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            logger.info(f'[FSM] Расшифрованный текст: {text}')
            recognized_msg = get_local_message("socratic_voice_recognized") or "Ваше сообщение:"
            await message.answer(f'{recognized_msg}\n[ {text} ]')
            await process_answer(message, state, text)
    except sr.UnknownValueError:
        error_msg = get_local_message("socratic_error_voice") or "Не удалось распознать речь."
        await message.answer(error_msg)
    except sr.RequestError as e:
        error_msg = get_local_message("socratic_error_processing") or "Ошибка сервиса распознавания речи."
        await message.answer(error_msg)
    finally:
        for path in [temp_ogg_path, wav_path]:
            try:
                os.remove(path)
            except Exception as e:
                logger.error(f'[FSM] Ошибка при удалении временных файлов: {e}')

@router.message(SocraticFSM.waiting_for_answer)
async def handle_text_socratic_answer(message: types.Message, state: FSMContext):
    """Обработка текстового ответа"""
    await process_answer(message, state, message.text)
