from aiogram import Router, types, F
from ..keyboards import (
    request_keyboard,
    voice_subscription_keyboard,
    start_diag_keyboard,
    diagnostics_state_keyboard,
    detailed_state_keyboard,
)
router = Router()

# --- Ветка 1: Да, у меня есть запрос ---
@router.callback_query(F.data == "has_request")
async def has_request_handler(query: types.CallbackQuery):
    text = (
        "Отлично. Вы можете:\n"
        "— ✏️ Написать свой запрос в виде текста (бесплатно)\n"
        "— 🎙 Записать голосом (до 5 минут) — для этого нужна подписка"
    )
    await query.message.answer(text, reply_markup=request_keyboard())
    await query.answer()

@router.callback_query(F.data == "request_text")
async def request_text_handler(query: types.CallbackQuery):
    await query.message.answer("Пожалуйста, отправьте ваш запрос текстом:")
    await query.answer()

@router.callback_query(F.data == "enable_voice")
async def enable_voice_handler(query: types.CallbackQuery):
    text = (
        "Голосом часто проще: можно просто рассказать как другу, что сейчас тревожит.\n"
        "Мы расшифруем, проанализируем и создадим мантру лично под вас."
    )
    await query.message.answer(text, reply_markup=voice_subscription_keyboard())
    await query.answer()

# --- Ветка 2: Хочу сначала разобраться (экспресс-диагностика) ---
@router.callback_query(F.data == "explore_inside")
async def explore_inside_handler(query: types.CallbackQuery):
    text = (
        "Тогда давайте начнём с небольшой внутренней диагностики — как сканирование.\n"
        "Это займёт пару минут и поможет понять, что сейчас важнее всего.\n"
        "Мы вместе определим, с чего стоит начать, и вы получите анализ и мантру, подходящую именно вам."
    )
    await query.message.answer(text, reply_markup=start_diag_keyboard())
    await query.answer()

@router.callback_query(F.data == "start_diagnostics")
async def start_diagnostics_handler(query: types.CallbackQuery):
    await query.message.answer(
        "Что ты чаще всего ощущаешь в последнее время — внутри себя, в фоне?",
        reply_markup=diagnostics_state_keyboard()
    )
    await query.answer()

@router.callback_query(F.data.in_(["diag_negative", "diag_neutral", "diag_positive"]))
async def diagnostic_state_detail(query: types.CallbackQuery):
    state = query.data
    if state == "diag_negative":
        options = [
            ("😟 Тревожность, страх", "block_emotion"),
            ("😞 Самокритика, «я не такой»", "block_selfesteem"),
            ("🔁 Прокрастинация, застревание", "block_behavior"),
            ("💔 Ощущение одиночества, непринятости", "block_relationship"),
            ("😐 Апатия, пустота", "block_meaning"),
            ("😠 Раздражение, подавленный гнев", "block_emotion2"),
            ("😰 Стыд, вина, чувство «неправильности»", "block_selfesteem2"),
        ]
    elif state == "diag_neutral":
        options = [
            ("🌫 Непонятное внутреннее напряжение", "block_emotion"),
            ("😶 «Ничего не чувствую» / подавление", "block_behavior"),
            ("⏳ Автоматизм, «как будто всё по инерции»", "block_behavior2"),
            ("🤔 Хочу понять, в чём я застрял(а)", "block_behavior3"),
            ("😬 Чувствую, что что-то не так, но не знаю что", "block_selfesteem"),
            ("🧍 Живу «рядом с собой», нет включённости", "block_meaning"),
            ("🤷 «Вроде всё норм, но пусто»", "block_meaning2"),
        ]
    else:  # diag_positive
        options = [
            ("✨ Хочу глубже понять себя", "block_meaning"),
            ("💡 Понимаю, что пора пересмотреть установки", "block_selfesteem"),
            ("🌱 В процессе перемен, но хочу ясности", "block_emotion"),
            ("🔍 Наблюдаю за собой — хочется ясности", "block_behavior"),
            ("💬 Хочу переформулировать свой внутренний диалог", "block_relationship"),
            ("🧘 Хочу больше внутренней опоры, даже в хорошем состоянии", "block_meaning2"),
            ("🎯 Интересно: какие у меня когнитивные ловушки?", "block_cbt"),
        ]
    await query.message.answer(
        "Пожалуйста, выберите, что ближе всего к вашему состоянию:",
        reply_markup=detailed_state_keyboard(options)
    )
    await query.answer()

# @router.callback_query(F.data.regexp(r"^block_"))
# async def start_socratic_by_block(query: types.CallbackQuery):
#     # Здесь можно записать выбранный блок в state/context, если нужно
#     await query.message.answer(
#         "Спасибо! Сейчас начнем небольшое исследование этого состояния. Готовьте честные ответы — дальше будет серия персональных вопросов от ИИ ✨"
#     )
#     # Тут должен запускаться сократический диалог по нужному блоку (логика добавляется дальше)
#     await query.answer()
