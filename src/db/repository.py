from pathlib import Path
from typing import List, Optional

import aiosqlite

from settings import get_logger

logger = get_logger(__name__)


class GptThreadRepository:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    async def get_thread_id(self, tg_user_id: int, mode: str) -> Optional[str]:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON;")

                cursor = await db.execute(
                    """
                    SELECT openai_thread_id FROM gpt_sessions
                    WHERE tg_user_id = ? AND mode = ?
                    """,
                    (tg_user_id, mode)
                )
                row = await cursor.fetchone()

                return row[0] if row else None
        except aiosqlite.Error as e:
            logger.error(f"Database Error (get_thread_id): {e}")
            raise

    async def create_thread(self, tg_user_id: int, mode: str, openai_thread_id: str) -> None:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON;")

                await db.execute(
                    """
                    INSERT INTO gpt_sessions (tg_user_id, mode, openai_thread_id)
                    VALUES (?, ?, ?)
                    """,
                    (tg_user_id, mode, openai_thread_id)
                )
                await db.commit()
        except aiosqlite.Error as e:
            logger.error(f"Database Error (create_thread): {e}")
            raise

    async def add_message(self, openai_thread_id: str, role: str, content: str) -> None:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    """
                    INSERT INTO gpt_messages (openai_thread_id, role, content)
                    VALUES (?, ?, ?)
                    """,
                    (openai_thread_id, role, content)
                )
                await db.commit()
        except aiosqlite.Error as e:
            logger.error(f"Database Error (add_message): {e}")
            raise

    async def get_messages(self, openai_thread_id: str) -> List[dict]:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT role, content FROM gpt_messages
                    WHERE openai_thread_id = ?
                    ORDER BY created_at
                    """,
                    (openai_thread_id,)
                )
                rows = await cursor.fetchall()

            return [{"role": row[0], "content": row[1]} for row in rows]
        except aiosqlite.Error as e:
            logger.error(f"Database Error (get_messages): {e}")
            raise

    async def clear_thread(self, openai_thread_id: str) -> None:
        try:
            async with aiosqlite.connect(self._db_path) as db:
                await db.execute(
                    "DELETE FROM gpt_messages WHERE openai_thread_id = ?",
                    (openai_thread_id,)
                )
                await db.commit()
        except aiosqlite.Error as e:
            logger.error(f"Database Error (clear_thread): {e}")
            raise
