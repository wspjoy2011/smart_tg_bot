from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)

from bot.commands import start, random, gpt
from bot.handlers.gpt_handler import gpt_message_handler
from db.initializer import DatabaseInitializer
from db.repository import GptThreadRepository
from services import OpenAIClient
from settings.config import config


def main():
    """
    Starts the Telegram bot application.

    This function initializes the local SQLite database, sets up the OpenAI client,
    registers command and message handlers for the Telegram bot, and starts polling updates.

    Handlers:
       - /start: Initializes the bot interface.
       - /random: Triggers the assistant to return a random technical fact.
       - /gpt: Enables short-response GPT assistant mode.
       - MessageHandler: Handles free-form text input when in GPT mode.
       - CallbackQueryHandler: Supports menu button interactions for "start" and "random".

    Environment:
       Requires the following values from the config:
           - OpenAI API key and model settings
           - Telegram bot token
           - Path to SQLite database

    Raises:
       RuntimeError: If bot fails to start due to misconfiguration or API error.
    """
    db_initializer = DatabaseInitializer(config.path_to_db)
    db_initializer.create_tables()

    thread_repository = GptThreadRepository(config.path_to_db)

    openai_client = OpenAIClient(
        openai_api_key=config.openai_api_key,
        model=config.openai_model,
        temperature=config.openai_model_temperature
    )

    app = ApplicationBuilder().token(config.tg_bot_api_key).build()

    app.bot_data["openai_client"] = openai_client
    app.bot_data["thread_repository"] = thread_repository

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random))
    app.add_handler(CommandHandler("gpt", gpt))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), gpt_message_handler))

    app.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(random, pattern="^random$"))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
