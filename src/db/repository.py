from pathlib import Path

import aiosqlite


class GptSessionRepository:
    def __init__(self, db_path: Path):
        self._db_path = db_path

    async def get_or_create_session(self, tg_user_id: int, mode: str) -> int:
        """Get the ID of an existing session or create a new one if it doesn't exist."""

    async def add_message(self, session_id: int, role: str, content: str) -> None:
        """Save a message (question or response) to the database."""

    async def get_messages(self, session_id: int) -> list[dict]:
        """Retrieve all messages for the session in the format {'role': ..., 'content': ...}."""

    async def clear_session(self, session_id: int) -> None:
        """Delete all messages related to a session (optional reset)."""
