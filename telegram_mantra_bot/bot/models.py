# bot/models.py

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    ForeignKey, TIMESTAMP, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker, Session
from .config import load_config
from datetime import datetime

config = load_config()

# Create database engine
engine = create_engine(config.database_url, echo=False, future=True)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    mantras = relationship("Mantra", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")


class Mantra(Base):
    __tablename__ = 'mantras'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    user = relationship("User", back_populates="mantras")
    audio_orders = relationship("AudioOrder", back_populates="mantra", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="mantra")


class AudioOrder(Base):
    __tablename__ = 'audio_orders'
    id = Column(Integer, primary_key=True)
    mantra_id = Column(Integer, ForeignKey('mantras.id', ondelete='CASCADE'), nullable=False)
    user_record = Column(Boolean, default=False)
    voice_artist_id = Column(Integer)
    status = Column(String(50), default='pending')
    file_url = Column(Text)
    ordered_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    mantra = relationship("Mantra", back_populates="audio_orders")


class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    mantra_id = Column(Integer, ForeignKey('mantras.id', ondelete='SET NULL'))
    remind_at = Column(TIMESTAMP, nullable=False)
    sent = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="reminders")
    mantra = relationship("Mantra", back_populates="reminders")


def get_or_create_user(telegram_id: int, username: str = None) -> User:
    """Get existing user or create new one"""
    session = SessionLocal()
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
    
    session.close()
    return user


def get_user_mantras(telegram_id: int) -> list:
    """Get list of user's mantras"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return []
        return [(m.id, m.text) for m in user.mantras]
    finally:
        db.close()


def get_mantra(mantra_id: int):
    """Get mantra by ID"""
    db = SessionLocal()
    try:
        return db.query(Mantra).filter(Mantra.id == mantra_id).first()
    finally:
        db.close()


def save_mantra(telegram_id: int, text: str) -> Mantra:
    """Save new mantra for user"""
    session = SessionLocal()
    
    # Get or create user
    user = session.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.flush()
    
    # Create mantra
    mantra = Mantra(user_id=user.id, text=text)
    session.add(mantra)
    session.commit()
    session.refresh(mantra)
    
    session.close()
    return mantra


def delete_mantra(mantra_id: int) -> bool:
    """Delete mantra by ID"""
    db = SessionLocal()
    try:
        mantra = db.query(Mantra).filter(Mantra.id == mantra_id).first()
        if not mantra:
            return False
        db.delete(mantra)
        db.commit()
        return True
    finally:
        db.close()


def schedule_reminder(db, telegram_id: int, mantra_id: int, remind_at: datetime):
    """Schedule reminder for mantra"""
    user = get_or_create_user(telegram_id)
    reminder = Reminder(
        user_id=user.id,
        mantra_id=mantra_id,
        remind_at=remind_at
    )
    db.add(reminder)
    db.commit()
    return reminder


# Create all tables
Base.metadata.create_all(bind=engine)
