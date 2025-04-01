import sqlite3
from pathlib import Path


class DatabaseInitializer:
    """
    Initializes the SQLite database and creates necessary tables.

    This class sets up the required schema for managing GPT conversation sessions
    and storing message history, including OpenAI thread associations.

    Attributes:
        _db_path (Path): Path to the SQLite database file.
    """

    def __init__(self, db_path: Path):
        """
        Initializes the DatabaseInitializer.

        Args:
            db_path (Path): Path to the SQLite database file.
        """
        self._db_path = db_path

    def create_tables(self) -> None:
        """
        Creates the `gpt_sessions` and `gpt_messages` tables if they don't exist.

        - `gpt_sessions` stores user IDs, conversation modes, and OpenAI thread IDs.
        - `gpt_messages` stores messages associated with a thread (user/system/assistant).

        Raises:
            sqlite3.Error: If an error occurs during table creation.
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gpt_sessions (
                    id INTEGER PRIMARY KEY,
                    tg_user_id INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    openai_thread_id TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(tg_user_id, mode)
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gpt_messages (
                    id INTEGER PRIMARY KEY,
                    openai_thread_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(openai_thread_id) REFERENCES gpt_sessions(openai_thread_id) ON DELETE CASCADE
                );
            """)

            conn.commit()
