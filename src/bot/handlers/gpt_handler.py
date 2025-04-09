from openai import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

from bot.message_sender import send_html_message
from bot.utils.openai_threads import get_or_create_thread_id
from db.enums import SessionMode, MessageRole
from db.repository import GptThreadRepository
from services import OpenAIClient
from settings import config, get_logger

logger = get_logger(__name__)


async def gpt_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user messages in GPT mode.

    This function processes free-form text messages sent by the user when the GPT mode is active.
    It ensures that each user has a corresponding OpenAI thread and stores the conversation history.
    The assistant responses concisely, and all messages are saved to the local database.

    Args:
        update (telegram.Update): The incoming update from the Telegram user.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Context object containing bot and user data.

    Raises:
        openai.OpenAIError: If the assistant fails to process the message or respond.

    Side Effects:
        - Sends a message back to the user containing the assistant's reply.
        - Stores both the user message and assistant reply in the SQLite database.
        - Creates a new OpenAI thread if one doesn't exist for the current user and mode.
    """
    mode = context.user_data.get("mode")
    if mode != SessionMode.GPT.value:
        return

    user_message = update.message.text
    tg_user_id = update.effective_user.id

    openai_client: OpenAIClient = context.bot_data["openai_client"]
    thread_repository: GptThreadRepository = context.bot_data["thread_repository"]

    thread_id = await get_or_create_thread_id(tg_user_id, mode, thread_repository, openai_client)

    await thread_repository.add_message(thread_id, role=MessageRole.USER.value, content=user_message)

    try:
        assistant_id = config.ai_assistant_fact_spark_id
        reply = await openai_client.ask(
            assistant_id=assistant_id,
            thread_id=thread_id,
            user_message=user_message
        )
    except OpenAIError as e:
        logger.warning(f"Assistant failed in GPT mode: {e}")
        await update.message.reply_text("Assistant failed to respond. Please try again later.")
        return

    await thread_repository.add_message(thread_id, role=MessageRole.ASSISTANT.value, content=reply)

    await send_html_message(update, context, reply)
