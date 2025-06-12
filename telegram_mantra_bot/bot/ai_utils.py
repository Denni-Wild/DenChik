import openai
import asyncio
from .config import load_config

async def generate_socratic_questions_openrouter(block, description, openrouter_api_key, num_questions=6):
    config = load_config()
    openai.api_key = openrouter_api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    model_name = "mistralai/mixtral-8x7b-instruct"
    prompt = config.socratic_prompt.format(
        num_questions=num_questions,
        block=block,
        description=description
    )
    loop = asyncio.get_running_loop()
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
    questions = [q.strip("-—. 1234567890) ") for q in questions_text.split('\n') if q.strip()]
    return [q for q in questions if q][:num_questions]

async def generate_next_socratic_question_openrouter(user_request, history, openrouter_api_key):
    """
    user_request: str — исходный запрос пользователя
    history: list of (question, answer) tuples
    Возвращает следующий вопрос (str)
    """
    config = load_config()
    openai.api_key = openrouter_api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    model_name = "mistralai/mixtral-8x7b-instruct"
    # Формируем историю
    history_text = ""
    for idx, (q, a) in enumerate(history, 1):
        history_text += f"Вопрос {idx}: {q}\nОтвет {idx}: {a}\n"
    prompt = (
        f"Ты — полезный ассистент, задаёшь вопросы для психологической саморефлексии.\n"
        f"Исходный запрос пользователя: {user_request}\n"
        f"История диалога:\n{history_text}"
        f"Сформулируй следующий сократический вопрос для пользователя. Только вопрос, без пояснений."
    )
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None,
        lambda: openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Ты — полезный ассистент, задаёшь вопросы для психологической саморефлексии."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
        )
    )
    question = response["choices"][0]["message"]["content"].strip()
    return question 