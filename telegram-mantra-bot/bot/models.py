# bot/models.py

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    ForeignKey, TIMESTAMP, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker, Session
from .config import load_config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())

    topics = relationship("Topic", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    current_step = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="topics")
    answers = relationship("Answer", back_populates="topic")
    mantras = relationship("Mantra", back_populates="topic")


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    question_index = Column(Integer, nullable=False)
    answer_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    topic = relationship("Topic", back_populates="answers")


class Mantra(Base):
    __tablename__ = 'mantras'
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    step_index = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    topic = relationship("Topic", back_populates="mantras")
    audio_orders = relationship("AudioOrder", back_populates="mantra")
    reminders = relationship("Reminder", back_populates="mantra")


class AudioOrder(Base):
    __tablename__ = 'audio_orders'
    id = Column(Integer, primary_key=True)
    mantra_id = Column(Integer, ForeignKey('mantras.id', ondelete='CASCADE'), nullable=False)
    user_record = Column(Boolean, default=False)
    voice_artist_id = Column(Integer)
    status = Column(String(50), default='pending')
    file_url = Column(Text)
    ordered_at = Column(TIMESTAMP, server_default=func.now())

    mantra = relationship("Mantra", back_populates="audio_orders")


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), default='RUB')
    payment_type = Column(String(50))  # 'one_time' or 'subscription'
    status = Column(String(50), default='pending')
    provider_payment_id = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="payments")


class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    mantra_id = Column(Integer, ForeignKey('mantras.id', ondelete='SET NULL'))
    remind_at = Column(TIMESTAMP, nullable=False)
    sent = Column(Boolean, default=False)

    user = relationship("User", back_populates="reminders")
    mantra = relationship("Mantra", back_populates="reminders")


def get_or_create_user(db: Session, telegram_id: int, username: str = None) -> User:
    """
    Найти пользователя по telegram_id или создать нового.
    Возвращает экземпляр User.
    """
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# Настройка подключения к базе и фабрика сессий

config = load_config()
engine = create_engine(config.db_url, echo=False, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
