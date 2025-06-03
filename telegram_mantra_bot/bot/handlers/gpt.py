# bot/handlers/gpt.py

from aiogram import Router, types, F
from datetime import datetime, timedelta
from ..config import load_config
from ..models import SessionLocal, Mantra, Reminder, Topic, Answer, User
from .reminders import schedule_reminder
from ..keyboards import get_mantra_keyboard
import openai
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


async def generate_mantra(message: types.Message, state_data: dict):
    """
    Основная логика генерации мантры
    """
    try:
        logger.info("Начинаем генерацию мантры...")
        
        # Загружаем конфиг и ключ
        config = load_config()
        openai.api_key = config.openrouter_api_key
        openai.api_base = "https://openrouter.ai/api/v1"
        logger.info(f"OpenRouter API настроен, base_url: {openai.api_base}")

        # Получаем ответы из state
        socratic_answers = state_data.get("socratic_answers", [])
        logger.info(f"Получены ответы из state: {len(socratic_answers)} ответов")
        if not socratic_answers:
            logger.error("Ответы не найдены в state_data!")
            await message.answer("Не удалось найти ответы для генерации мантры.")
            return

        # Создаем новую тему и сохраняем ответы
        db = SessionLocal()
        logger.info("Подключились к БД")
        
        try:
            # Создаем запись пользователя, если её нет
            user = db.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                logger.info(f"Создаем нового пользователя с telegram_id={message.from_user.id}")
                user = User(telegram_id=message.from_user.id)
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                logger.info(f"Найден существующий пользователь id={user.id}")

            # Создаем новую тему
            topic = Topic(
                user_id=user.id,
                title="Персональная мантра",
                current_step=1
            )
            db.add(topic)
            db.commit()
            db.refresh(topic)
            logger.info(f"Создана новая тема id={topic.id}")

            # Сохраняем ответы
            for idx, answer_text in enumerate(socratic_answers):
                answer = Answer(
                    topic_id=topic.id,
                    question_index=idx,
                    answer_text=answer_text
                )
                db.add(answer)
            db.commit()
            logger.info(f"Сохранены все {len(socratic_answers)} ответов")

            # Формируем промпт для GPT
            prompt = (
                config.gpt_prefix
                + "\n".join(socratic_answers)
                + config.gpt_suffix
            )
            logger.info("Сформирован промпт для GPT")
            logger.info(f"Промпт:\n{prompt}")

            # Запрос к OpenRouter API
            logger.info("Отправляем запрос к OpenRouter API...")
            try:
                resp = openai.ChatCompletion.create(
                    model="deepseek/deepseek-r1:free",
                    messages=[
                        {"role": "system", "content": "Ты — эксперт по созданию персональных мантр, которые помогают людям трансформировать их состояние."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    headers={"HTTP-Referer": "https://github.com/your-repo/telegram-mantra-bot"}
                )
                logger.info("Получен ответ от OpenRouter API")
                logger.info(f"Полный ответ API: {resp}")
                
                mantra_text = resp.choices[0].message.content.strip()
                logger.info(f"Сгенерирована мантра: {mantra_text}")
            except Exception as e:
                logger.error(f"Ошибка при запросе к OpenRouter API: {str(e)}")
                await message.answer("Произошла ошибка при генерации мантры. Пожалуйста, попробуйте позже.")
                return

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
            logger.info(f"Мантра сохранена в БД с id={mantra.id}")

            # Планируем напоминание через 24 часа
            remind_at = datetime.utcnow() + timedelta(hours=24)
            schedule_reminder(db, message.from_user.id, mantra.id, remind_at)
            logger.info("Напоминание запланировано")

            # Отправляем пользователю текст мантры
            await message.answer(
                f"✨ Вот ваша персональная мантра:\n\n{mantra_text}",
                reply_markup=get_mantra_keyboard()
            )
            logger.info("Мантра отправлена пользователю с кнопками действий")

        except Exception as db_error:
            logger.error(f"Ошибка при работе с БД: {str(db_error)}")
            await message.answer("Произошла ошибка при сохранении данных. Пожалуйста, попробуйте позже.")
        finally:
            db.close()
            logger.info("Соединение с БД закрыто")

    except Exception as e:
        logger.error(f"Необработанная ошибка в generate_mantra: {str(e)}")
        await message.answer("Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже.")


@router.callback_query(F.data == "generate_mantra")
async def generate_mantra_handler(query: types.CallbackQuery, state: dict):
    """
    Обработчик для генерации мантры через callback query
    """
    logger.info("Получен callback query для генерации мантры")
    await generate_mantra(query.message, state)
