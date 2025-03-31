from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler
)

from bot.commands import start, random
from db.initializer import DatabaseInitializer
from db.repository import GptThreadRepository
from services import OpenAIClient
from settings.config import config


def main():
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

    app.add_handler(CallbackQueryHandler(start, pattern="^start$"))
    app.add_handler(CallbackQueryHandler(random, pattern="^random$"))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
