"""Configuration module for environment variables and paths.

This module defines application-wide settings using Pydantic's BaseSettings,
including API keys, model parameters, resource paths, and storage locations.
Settings are automatically loaded from a `.env` file at the project root.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class AppConfig(BaseSettings):
    """
    Application configuration using environment variables and defaults.

    Attributes:
        openai_api_key (str): OpenAI API key for accessing the Assistant API.
        tg_bot_api_key (str): Telegram Bot API key from BotFather.
        ai_assistant_random_facts_id (str): Assistant ID for random fact generation.
        ai_assistant_fact_spark_id (str): Assistant ID for short GPT answers.

        openai_model (str): Name of the OpenAI model to use.
        openai_model_temperature (float): Temperature for response creativity.

        path_to_messages (Path): Path to directory containing HTML message templates.
        path_to_images (Path): Path to image assets (e.g., for UI).
        path_to_menus (Path): Path to JSON files defining menu buttons.
        path_to_prompts (Path): Path to text files for assistant instructions.

        path_to_logs (Path): Path to store application logs.
        path_to_db (Path): Path to SQLite database for thread/message history.

        model_config (SettingsConfigDict): Pydantic settings for loading `.env` file.
    """

    openai_api_key: str
    tg_bot_api_key: str
    ai_assistant_random_facts_id: str
    ai_assistant_fact_spark_id: str

    openai_model: str = "gpt-3.5-turbo"
    openai_model_temperature: float = 1.5

    path_to_messages: Path = BASE_DIR / "resources" / "messages"
    path_to_images: Path = BASE_DIR / "resources" / "images"
    path_to_menus: Path = BASE_DIR / "resources" / "menus"
    path_to_prompts: Path = BASE_DIR / "resources" / "prompts"

    path_to_logs: Path = BASE_DIR / "logs"
    path_to_db: Path = BASE_DIR / "storage" / "chat_sessions.db"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8"
    )


config = AppConfig()
