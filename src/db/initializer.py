import sqlite3
from pathlib import Path


class DatabaseInitializer:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    def create_tables(self) -> None:
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
