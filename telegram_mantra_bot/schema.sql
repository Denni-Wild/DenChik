CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL
);
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title TEXT,
    current_step INTEGER DEFAULT 1
);
CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    question_index INTEGER,
    answer_text TEXT
);
CREATE TABLE mantras (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id),
    text TEXT,
    step_index INTEGER
);
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    mantra_id INTEGER REFERENCES mantras(id),
    remind_at TIMESTAMP,
    sent BOOLEAN DEFAULT FALSE
);
