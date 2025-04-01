from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class AppConfig(BaseSettings):
    openai_api_key: str
    tg_bot_api_key: str
    ai_assistant_random_facts_id: str
    ai_assistant_fact_spark_id: str

    openai_model: str = "gpt-3.5-turbo"
    openai_model_temperature: float = 1.5

    path_to_messages: Path =  BASE_DIR / "resources" / "messages"
    path_to_images: Path =  BASE_DIR / "resources" / "images"
    path_to_menus: Path = BASE_DIR / "resources" / "menus"
    path_to_prompts: Path = BASE_DIR / "resources" / "prompts"

    path_to_logs: Path = BASE_DIR / "logs"

    path_to_db: Path = BASE_DIR / "storage" / "chat_sessions.db"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8"
    )


config = AppConfig()
