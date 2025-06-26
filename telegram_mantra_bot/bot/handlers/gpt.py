# bot/handlers/gpt.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from ..config import load_config
from ..models import save_mantra
from ..keyboards import main_menu_keyboard
import openai
import logging
from dotenv import load_dotenv
import tempfile, os, subprocess, speech_recognition as sr

# Загружаем переменные из .env
load_dotenv()

# Настраиваем логгер для этого модуля
logger = logging.getLogger(__name__)

# Настраиваем OpenRouter API
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = load_config().openrouter_api_key
AI_MODEL = load_config().ai_model

router = Router()

class MantraCreationStates(StatesGroup):
    waiting_for_request = State()
    waiting_for_feelings = State()

@router.callback_query(F.data == "has_request")
async def handle_has_request(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик наличия запроса у пользователя"""
    logger.info("Пользователь указал, что у него есть запрос")
    await callback.message.edit_text(
        "Пожалуйста, опишите ваш запрос или чувство, с которым хотите поработать.\n"
        "Это может быть что угодно: тревога, неуверенность, желание изменений...\n\n"
        "Напишите всё, что считаете важным ✨"
    )
    await state.set_state(MantraCreationStates.waiting_for_request)
    await callback.answer()

@router.callback_query(F.data == "explore_inside")
async def handle_explore_inside(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик желания разобраться в чувствах"""
    logger.info("Пользователь хочет разобраться в своих чувствах")
    await callback.message.edit_text(
        "Давайте вместе исследуем ваше состояние.\n\n"
        "Пожалуйста, выберите, что ближе всего к вашему состоянию:",
        reply_markup=diagnostics_state_keyboard()
    )
    await callback.answer()

@router.message(MantraCreationStates.waiting_for_request, F.text)
async def handle_request(message: types.Message, state: FSMContext):
    """Обработчик получения текстового запроса"""
    logger.info("Получен текстовый запрос пользователя")
    logger.info(f'Текст запроса пользователя {message.from_user.id}: {message.text}')
    await generate_mantra(message, {"request": message.text})
    await state.clear()

@router.message(MantraCreationStates.waiting_for_feelings, F.text)
async def handle_feelings(message: types.Message, state: FSMContext):
    """Обработчик получения текстового описания чувств"""
    logger.info("Получено текстовое описание чувств пользователя")
    await generate_mantra(message, {"feelings": message.text})
    await state.clear()

@router.message(MantraCreationStates.waiting_for_request, F.voice)
@router.message(MantraCreationStates.waiting_for_feelings, F.voice)
async def handle_voice_request(message: types.Message, state: FSMContext):
    """Обработчик получения голосового сообщения в любом состоянии создания мантры"""
    current_state = await state.get_state()
    logger.info(f'[VOICE] Получено голосовое сообщение в состоянии {current_state} от пользователя {message.from_user.id}')
    
    if message.voice.duration == 0:
        logger.warning(f'[VOICE] Получено пустое голосовое сообщение от пользователя {message.from_user.id}')
        await message.answer('Похоже, сообщение пустое. Пожалуйста, повторите голосовой ответ.')
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = os.path.join(tmpdir, 'voice.ogg')
        wav_path = os.path.join(tmpdir, 'voice.wav')
        
        logger.info(f'[VOICE] Скачиваем голосовое сообщение для пользователя {message.from_user.id}')
        file = await message.bot.get_file(message.voice.file_id)
        await message.bot.download(file, destination=ogg_path)
        
        try:
            logger.info(f'[VOICE] Конвертируем голосовое сообщение в WAV для пользователя {message.from_user.id}')
            subprocess.run(['ffmpeg', '-y', '-i', ogg_path, wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f'[VOICE] Ошибка конвертации аудио для пользователя {message.from_user.id}: {str(e)}')
            await message.answer('Ошибка конвертации аудио. Проверьте, установлен ли ffmpeg.')
            return

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            logger.info(f'[VOICE] Начинаем распознавание речи для пользователя {message.from_user.id}')
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='ru-RU')
                logger.info(f'[VOICE] Успешно распознан текст для пользователя {message.from_user.id}: {text}')
                await message.answer(f'Ваше сообщение:\n[ {text} ]')
                
                # Генерируем мантру на основе распознанного текста
                await generate_mantra(message, {"request": text})
                await state.clear()
                
            except sr.UnknownValueError:
                logger.error(f'[VOICE] Не удалось распознать речь для пользователя {message.from_user.id}')
                await message.answer('Не удалось распознать речь. Пожалуйста, попробуйте еще раз или отправьте текстовое сообщение.')
            except sr.RequestError as e:
                logger.error(f'[VOICE] Ошибка сервиса распознавания для пользователя {message.from_user.id}: {str(e)}')
                await message.answer('Ошибка сервиса распознавания. Пожалуйста, попробуйте позже или отправьте текстовое сообщение.')

async def generate_mantra(message: types.Message, state_data: dict):
    """Генерация персональной мантры"""
    logger.info("Начинаем генерацию мантры")
    config = load_config()
    try:
        # Формируем промпт в зависимости от типа входных данных
        if "request" in state_data:
            prompt = config.mantra_prompt.format(request=state_data['request'])
        else:
            prompt = (
                "Создай персональную мантру на основе описания чувств пользователя. "
                "Мантра должна быть краткой, позитивной и помогать трансформировать текущее состояние. "
                f"Описание чувств: {state_data['feelings']}"
            )
        resp = openai.ChatCompletion.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "Ты — эксперт по созданию персональных мантр, которые помогают людям трансформировать их состояние."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            headers={"HTTP-Referer": "https://github.com/your-repo/telegram-mantra-bot"}
        )
        logger.info("Получен ответ от OpenRouter API")
        mantra_text = resp.choices[0].message.content.strip()
        logger.info(f"Сгенерирована мантра: {mantra_text}")
        
        # Сохраняем мантру
        mantra = save_mantra(message.from_user.id, mantra_text)
        logger.info(f"Мантра сохранена в БД с id={mantra.id}")
        
        # Отправляем пользователю текст мантры
        await message.answer(
            f"✨ Вот ваша персональная мантра:\n\n{mantra_text}",
            reply_markup=main_menu_keyboard()
        )
        logger.info("Мантра отправлена пользователю")
            
    except Exception as e:
        logger.error(f"Ошибка при генерации мантры: {str(e)}")
        await message.answer("Произошла ошибка при генерации мантры. Пожалуйста, попробуйте позже.")

@router.callback_query(F.data == "generate_mantra")
async def generate_mantra_handler(query: types.CallbackQuery, state: FSMContext):
    """
    Обработчик для генерации мантры через callback query
    """
    logger.info("Получен callback query для генерации мантры")
    await generate_mantra(query.message, await state.get_data())
