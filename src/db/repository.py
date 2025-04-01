from pathlib import Path
from typing import List, Optional

import aiosqlite

from settings import get_logger

logger = get_logger(__name__)


class GptThreadRepository:
    """
    Repository for managing GPT threads and message history in SQLite.

    This class handles thread lookup/creation and stores all messages exchanged
    between the user and assistant in an OpenAI thread.

    Attributes:
        _db_path (Path): Path to the SQLite database.
    """

    def __init__(self, db_path: Path):
        """
        Initializes the repository with the given database path.

        Args:
            db_path (Path): Path to the SQLite database.
        """
        self._db_path = db_path

    async def get_thread_id(self, tg_user_id: int, mode: str) -> Optional[str]:
        """
        Returns the OpenAI thread ID for a user and mode, if it exists.

        Args:
            tg_user_id (int): Telegram user ID.
            mode (str): Chat mode (e.g. "gpt", "random").

        Returns:
            Optional[str]: The OpenAI thread ID if found, else None.

        Raises:
            aiosqlite.Error: If a database error occurs.
        """
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
        """
        Creates a new thread record in the database.

        Args:
            tg_user_id (int): Telegram user ID.
            mode (str): Chat mode.
            openai_thread_id (str): ID of the created OpenAI thread.

        Raises:
            aiosqlite.Error: If a database error occurs.
        """
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
        """
        Adds a message to the thread's message history.

        Args:
            openai_thread_id (str): OpenAI thread ID.
            role (str): Role of the message sender ("user", "assistant", "system").
            content (str): Message text content.

        Raises:
            aiosqlite.Error: If a database error occurs.
        """
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
        """
        Retrieves all messages for a given thread, ordered by time.

        Args:
            openai_thread_id (str): OpenAI thread ID.

        Returns:
            List[dict]: List of messages as dicts with 'role' and 'content'.

        Raises:
            aiosqlite.Error: If a database error occurs.
        """
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
        """Deletes all messages associated with a thread.

        Args:
            openai_thread_id (str): OpenAI thread ID.

        Raises:
            aiosqlite.Error: If a database error occurs.
        """
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
