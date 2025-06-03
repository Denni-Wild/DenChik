from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
router = Router()


class MantraRecordingStates(StatesGroup):
    waiting_for_voice = State()


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


@router.callback_query(F.data == "new_mantra")
async def handle_new_mantra(callback: types.CallbackQuery):
    """Обработчик запроса новой мантры"""
    logger.info("Пользователь хочет получить новую мантру")
    await callback.message.answer(
        "Хотите получить новую мантру? Давайте начнем с чистого листа ✨\n"
        "Выберите, как бы вы хотели продолжить:"
    )
    # TODO: Добавить кнопки выбора пути (сократический диалог или прямой запрос)
    await callback.answer()


@router.callback_query(F.data == "share_mantra")
async def handle_share_mantra(callback: types.CallbackQuery):
    """Обработчик кнопки поделиться мантрой"""
    logger.info("Пользователь хочет поделиться мантрой")
    share_text = (
        "🌟 Я получил персональную мантру от @your_bot_name!\n\n"
        "Попробуй и ты создать свою мантру для трансформации и роста ✨"
    )
    await callback.message.answer(
        f"Вот текст для sharing:\n\n{share_text}\n\n"
        "Скопируйте его и поделитесь с друзьями!"
    )
    await callback.answer()


@router.callback_query(F.data == "favorite_mantra")
async def handle_favorite_mantra(callback: types.CallbackQuery):
    """Обработчик сохранения мантры в избранное"""
    logger.info("Пользователь сохраняет мантру в избранное")
    # TODO: Добавить сохранение в БД
    await callback.message.answer(
        "✨ Мантра сохранена в избранное!\n"
        "Вы всегда можете найти её в разделе «Мои мантры»"
    )
    await callback.answer()


# Обработчик голосовых сообщений при записи мантры
@router.message(MantraRecordingStates.waiting_for_voice, F.voice)
async def handle_voice_message(message: types.Message, state: FSMContext):
    """Обработчик получения голосового сообщения с мантрой"""
    logger.info("Получено голосовое сообщение с мантрой")
    
    # TODO: Сохранить файл голосового сообщения
    
    await message.answer(
        "🎙 Ваша мантра успешно записана!\n"
        "Теперь вы можете прослушивать её в любой момент в разделе «Мои мантры»"
    )
    await state.clear()


# Обработчик текстовых сообщений при ожидании голосовой записи
@router.message(MantraRecordingStates.waiting_for_voice)
async def handle_wrong_voice_message(message: types.Message):
    """Обработчик неправильного формата сообщения при записи мантры"""
    await message.answer(
        "Пожалуйста, отправьте голосовое сообщение с вашей мантрой 🎙"
    ) 