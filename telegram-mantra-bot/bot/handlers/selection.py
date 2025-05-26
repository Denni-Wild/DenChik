# bot/handlers/selection.py

from aiogram import Router, types, F
from ..keyboards import (
    request_keyboard,
    voice_subscription_keyboard,
    diagnostics_keyboard
)

router = Router()


@router.callback_query(F.data == "has_request")
async def has_request_handler(query: types.CallbackQuery):
    """
    Ветка «Да, у меня есть запрос»
    Показываем варианты ввода собственного запроса
    """
    text = (
        "Отлично. Вы можете:\n"
        "— ✏️ Написать свой запрос в виде текста (бесплатно)\n"
        "— 🎙 Записать голосом (до 5 минут) — для этого нужна подписка"
    )
    await query.message.edit_text(text, reply_markup=request_keyboard())
    await query.answer()


@router.callback_query(F.data == "request_text")
async def request_text_handler(query: types.CallbackQuery):
    """
    Пользователь выбрал ввод текстом — просим отправить текст
    """
    await query.message.edit_text("Пожалуйста, отправьте ваш запрос текстом:")
    await query.answer()


@router.callback_query(F.data == "enable_voice")
async def enable_voice_handler(query: types.CallbackQuery):
    """
    Подключение голосовой отправки (требуется подписка)
    """
    text = (
        "Голосом часто проще: можно просто рассказать, как другу, что сейчас тревожит.\n"
        "Мы расшифруем, проанализируем и создадим мантру лично под вас."
    )
    await query.message.edit_text(text, reply_markup=voice_subscription_keyboard())
    await query.answer()


@router.callback_query(F.data == "explore_inside")
async def explore_inside_handler(query: types.CallbackQuery):
    """
    Ветка «Хочу сначала разобраться» — начало экспресс-диагностики
    """
    text = (
        "Тогда давайте начнём с небольшой внутренней диагностики — как сканирование.\n"
        "Это займёт пару минут и поможет понять, что сейчас важнее всего.\n"
        "Мы вместе определим, с чего стоит начать, и вы получите анализ и мантру, подходящую именно вам."
    )
    await query.message.edit_text(text, reply_markup=diagnostics_keyboard())
    await query.answer()


@router.callback_query(F.data == "start_diagnostics")
async def start_diagnostics_handler(query: types.CallbackQuery):
    """
    Пользователь запускает самодиагностику
    """
    # Здесь вы можете переключить состояние и начать задавать вопросы
    await query.message.edit_text("Запускаем самодиагностику…")
    await query.answer()
