"""
Database setup using SQLite (easily swappable to PostgreSQL).
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./genai_pulse.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)   # arxiv | huggingface | reddit | technews
    category = Column(String)                  # LLM | Vision | Audio | etc.
    published_at = Column(DateTime, default=datetime.utcnow)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_notified = Column(Boolean, default=False)
    score = Column(Integer, default=0)         # Reddit upvotes / HF likes / etc.
    authors = Column(Text)                     # JSON string


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=True)
    telegram_chat_id = Column(String, unique=True, nullable=True)
    slack_webhook = Column(String, nullable=True)
    sources = Column(Text, default="arxiv,huggingface,reddit,technews")
    frequency = Column(String, default="daily")  # daily | weekly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
