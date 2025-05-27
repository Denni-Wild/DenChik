# Telegram Mantra Bot

**Telegram-bot for generating and processing personal mantras** using AI and Socratic dialogue.

## Setup
1. Clone repo
2. Create `.env`:
   ```env
   BOT_TOKEN=<telegram token>
   OPENAI_API_KEY=<openai key>
   DATABASE_URL=postgresql://user:pass@localhost/db
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize DB:
   ```bash
   psql -f schema.sql
   ```
5. Run alembic migrations:
   ```bash
   alembic upgrade head
   ```
6. Launch bot:
   ```bash
   python -m bot.main
   ```

## Structure
```text
telegram-mantra-bot/
├── requirements.txt             # Dependency list
├── schema.sql                   # DB schema
├── alembic.ini & migrations/    # DB migrations
├── README.md                    # This documentation
├── bot/
│   ├── main.py                  # Инициализация Bot, Dispatcher, middleware, on_startup
│   ├── config.py                # Загрузка переменных окружения (dotenv)
│   ├── keyboards.py             # Функции: start_keyboard(), request_keyboard(), voice_subscription_keyboard(), diagnostics_keyboard()
│   └── handlers/
│       ├── start.py             # Обработчики: cmd_start(), cb_about(), cb_settings()
│       ├── selection.py         # Обработчики: has_request(), explore_inside(), start_diagnostics(), start_work(), topic_choice()
│       ├── socratic.py          # Обработчик: handle_answer() — задает вопросы и сохраняет ответы
│       ├── gpt.py               # Обработчик: generate_mantra() — генерация мантры через OpenAI и сохранение
│       └── reminders.py         # Функция: reminder_loop() — проверка и отправка напоминаний
└── models.py                    # ORM-модели SQLAlchemy: User, Topic, Answer, Mantra, Reminder
```
