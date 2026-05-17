import logging
import os
from typing import List

import aiosqlite

logger = logging.getLogger(__name__)

# Путь к файлу базы данных
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "ideas.db")


async def init_db() -> None:
    """
    Инициализирует базу данных: создаёт таблицу ideas, если её нет.
    Вызывается один раз при старте бота.
    """
    # Создаём директорию database/, если её нет
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                content    TEXT    NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    logger.info(f"БД инициализирована: {os.path.abspath(DB_PATH)}")


async def save_idea(content: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO ideas (content) VALUES (?)",
            (content,),
        )
        await db.commit()
        idea_id = cursor.lastrowid
    logger.info(f"Идея сохранена с id={idea_id}.")
    return idea_id


async def get_recent_ideas(limit: int = 30) -> List[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT content FROM ideas ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()

    ideas = [row[0] for row in rows]
    logger.info(f"Получено {len(ideas)} предыдущих идей из БД.")
    return ideas


async def get_ideas_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM ideas")
        row = await cursor.fetchone()
    return row[0] if row else 0