from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..keyboards import (
    mantra_keyboard, my_mantras_keyboard, main_menu_keyboard,
    start_request_keyboard, request_keyboard, get_mantra_keyboard
)
from ..models import get_user_mantras, save_mantra, delete_mantra, get_mantra
import logging
from typing import Union
import tempfile, os, subprocess, speech_recognition as sr

logger = logging.getLogger(__name__)
router = Router()


class MantraRecordingStates(StatesGroup):
    waiting_for_voice = State()


@router.message(F.text == "📂 Мои мантры")
async def show_mantras(message: types.Message):
    """Показать список мантр пользователя"""
    logger.info("Пользователь открывает список мантр")
    mantras = get_user_mantras(message.from_user.id)
    await message.answer(
        "Ваши персональные мантры:",
        reply_markup=my_mantras_keyboard(mantras)
    )


@router.message(F.text.in_(["➕ Новая мантра"]))
@router.callback_query(F.data == "start_new_mantra")
async def start_new_mantra(event: Union[types.Message, types.CallbackQuery]):
    """Начать создание новой мантры"""
    logger.info("Пользователь начинает создание новой мантры")
    text = "У вас уже есть какой-то внутренний запрос или чувство, с которым хотите поработать?"
    
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=start_request_keyboard())
        await event.answer()
    else:
        await event.answer(text, reply_markup=start_request_keyboard())


@router.callback_query(F.data == "back_to_mantras")
async def return_to_mantras(callback: types.CallbackQuery):
    """Вернуться к списку мантр"""
    logger.info("Пользователь возвращается к списку мантр")
    mantras = get_user_mantras(callback.from_user.id)
    await callback.message.edit_text(
        "Ваши персональные мантры:",
        reply_markup=my_mantras_keyboard(mantras)
    )


@router.callback_query(F.data == "back_to_main")
async def return_to_main(callback: types.CallbackQuery):
    """Вернуться в главное меню"""
    logger.info("Пользователь возвращается в главное меню")
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=main_menu_keyboard()
    )
    await callback.message.delete()


@router.callback_query(F.data == "back_to_request_start")
async def return_to_request_start(callback: types.CallbackQuery):
    """Вернуться к началу создания мантры"""
    logger.info("Пользователь возвращается к началу создания мантры")
    await callback.message.edit_text(
        "У вас уже есть какой-то внутренний запрос или чувство, с которым хотите поработать?",
        reply_markup=start_request_keyboard()
    )


@router.callback_query(F.data.startswith("mantra_"))
async def show_mantra(callback: types.CallbackQuery):
    """Показать конкретную мантру"""
    mantra_id = int(callback.data.split('_')[1])
    logger.info(f"Пользователь открывает мантру {mantra_id}")
    mantra = get_mantra(mantra_id)
    if not mantra:
        await callback.answer("Мантра не найдена")
        return
    
    await callback.message.edit_text(
        f"✨ Ваша мантра:\n\n{mantra.text}\n\n"
        "Выберите действие:",
        reply_markup=mantra_keyboard()
    )


@router.callback_query(F.data == "record_mantra")
async def handle_record_mantra(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик записи мантры голосом"""
    logger.info("Пользователь хочет записать мантру голосом")
    await callback.message.answer(
        "Пожалуйста, запишите вашу мантру голосовым сообщением. "
        "Говорите медленно и четко, чтобы мантра звучала гармонично ✨"
    )
    await state.set_state(MantraRecordingStates.waiting_for_voice)
    await callback.answer()


@router.message(MantraRecordingStates.waiting_for_voice, F.voice)
async def handle_voice_message(message: types.Message, state: FSMContext):
    """Обработчик получения голосового сообщения с мантрой"""
    logger.info(f'[FSM] Получено голосовое сообщение с мантрой от пользователя {message.from_user.id}')
    if message.voice.duration == 0:
        await message.answer('Похоже, сообщение пустое. Пожалуйста, запишите мантру ещё раз.')
        return
    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = os.path.join(tmpdir, 'voice.ogg')
        wav_path = os.path.join(tmpdir, 'voice.wav')
        file = await message.bot.get_file(message.voice.file_id)
        await message.bot.download(file, destination=ogg_path)
        try:
            subprocess.run(['ffmpeg', '-y', '-i', ogg_path, wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            await message.answer('Ошибка конвертации аудио. Проверьте, установлен ли ffmpeg.')
            return
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language='ru-RU')
                logger.info(f'[FSM] Расшифрованный текст голосового запроса пользователя {message.from_user.id}: {text}')
                await message.answer(f'Распознанный текст: {text}')
            except sr.UnknownValueError:
                await message.answer('Не удалось распознать речь.')
            except sr.RequestError:
                await message.answer('Ошибка сервиса распознавания.')
    await message.answer(
        "🎙 Ваша мантра успешно записана!\n"
        "Теперь вы можете прослушивать её в любой момент в разделе «Мои мантры»",
        reply_markup=mantra_keyboard()
    )
    await state.clear()


@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: types.Message):
    """Показать помощь"""
    logger.info("Пользователь запросил помощь")
    await message.answer(
        "🌟 Как работать с ботом:\n\n"
        "1. Нажмите «➕ Новая мантра»\n"
        "2. Опишите свой запрос или пройдите самодиагностику\n"
        "3. Ответьте на несколько вопросов\n"
        "4. Получите персональную мантру\n"
        "5. Практикуйте её регулярно\n\n"
        "Все ваши мантры сохраняются в разделе «📂 Мои мантры»\n\n"
        "Команды:\n"
        "/start - Начать сначала\n"
        "/help - Это сообщение\n"
        "/mantras - Мои мантры"
    )


@router.message(F.text == "💳 Подписка / Оплата")
async def show_subscription(message: types.Message):
    """Показать информацию о подписке"""
    logger.info("Пользователь смотрит информацию о подписке")
    await message.answer(
        "💫 Подписка открывает доступ к:\n"
        "- Голосовому вводу запросов\n"
        "- Профессиональной начитке мантр\n"
        "- Расширенной аналитике\n\n"
        "Стоимость:\n"
        "Месяц - 1000₽\n"
        "Год - 9000₽"
    )
    # TODO: Добавить кнопки оплаты


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: types.Message):
    """Показать настройки"""
    logger.info("Пользователь открывает настройки")
    await message.answer(
        "⚙️ Настройки:\n"
        "- Уведомления\n"
        "- Язык\n"
        "- Приватность"
    )
    # TODO: Добавить клавиатуру настроек


# --- Обработчики внутри мантры ---

@router.callback_query(F.data == "show_text")
async def show_mantra_text(callback: types.CallbackQuery):
    """Показать текст мантры"""
    logger.info("Пользователь просматривает текст мантры")
    # TODO: Получить текст мантры из БД
    await callback.message.edit_text(
        "✨ Текст вашей мантры:\n\n"
        "[Текст мантры]\n\n"
        "Как бы вы хотели продолжить?",
        reply_markup=mantra_keyboard()
    )


@router.callback_query(F.data == "play_recording")
async def play_mantra_recording(callback: types.CallbackQuery):
    """Воспроизвести запись мантры"""
    logger.info("Пользователь хочет прослушать запись мантры")
    # TODO: Получить и отправить аудиофайл
    await callback.message.answer("🎧 Ваша записанная мантра:")
    # TODO: Отправить аудио
    await callback.answer()


@router.callback_query(F.data == "edit_mantra")
async def edit_mantra(callback: types.CallbackQuery):
    """Редактировать текст мантры"""
    logger.info("Пользователь хочет отредактировать мантру")
    await callback.message.answer(
        "✏️ Введите новый текст мантры:"
    )
    # TODO: Добавить FSM для редактирования


@router.callback_query(F.data == "order_voiceover")
async def handle_order_voiceover(callback: types.CallbackQuery):
    """Обработчик заказа профессиональной начитки"""
    logger.info("Пользователь хочет заказать профессиональную начитку")
    await callback.message.answer(
        "🎧 Профессиональная начитка вашей мантры\n\n"
        "Стоимость: 500₽\n"
        "Срок выполнения: 24 часа\n\n"
        "В стоимость входит:\n"
        "- Начитка профессиональным диктором\n"
        "- Музыкальное сопровождение\n"
        "- Обработка звука\n"
        "- Файл в формате MP3"
    )
    # TODO: Добавить кнопку оплаты
    await callback.answer()


@router.callback_query(F.data == "delete_mantra")
async def delete_mantra(callback: types.CallbackQuery):
    """Удалить мантру"""
    logger.info("Пользователь хочет удалить мантру")
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить эту мантру?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, удалить", callback_data="confirm_delete"),
                InlineKeyboardButton(text="Нет, оставить", callback_data="cancel_delete")
            ]
        ])
    )


# Обработчик текстовых сообщений при ожидании голосовой записи
@router.message(MantraRecordingStates.waiting_for_voice)
async def handle_wrong_voice_message(message: types.Message):
    """Обработчик неправильного формата сообщения при записи мантры"""
    await message.answer(
        "Пожалуйста, отправьте голосовое сообщение с вашей мантрой 🎙"
    ) 