from openai import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import get_menu_buttons
from bot.message_sender import send_html_message, send_image_bytes, show_menu
from bot.resource_loader import load_message, load_image, load_menu
from db.enums import SessionMode, MessageRole
from db.repository import GptThreadRepository
from services import OpenAIClient
from settings import config, get_logger

logger = get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command and displays the main menu.

    Loads and sends the main welcome message, image, and keyboard with available bot commands.
    Also resets the user's current session mode.

    Args:
        update (telegram.Update): The incoming update from the Telegram user.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Context object containing bot and user data.

    Side Effects:
        - Sends a welcome image and message.
        - Displays a button-based menu to the user.
        - Resets context.user_data["mode"] to None.
    """
    context.user_data["mode"] = None

    text = await load_message("main")
    image_bytes = await load_image("main")
    menu_commands = await load_menu("main")

    await send_image_bytes(
        update=update,
        context=context,
        image_bytes=image_bytes,
    )

    await send_html_message(
        update=update,
        context=context,
        text=text,
    )

    await show_menu(
        update=update,
        context=context,
        commands=menu_commands
    )


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /random command to fetch a surprising technical fact.

    Ensures the user has a dedicated OpenAI thread for the random mode.
    Sends a technical trivia fact using the assistant, formats the response, and logs it to the database.

    Args:
        update (telegram.Update): The incoming update from the Telegram user.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Context object containing bot and user data.

    Raises:
        openai.OpenAIError: If the assistant fails to respond or run the completion.

    Side Effects:
        - Sends a formatted fact as an HTML message and image.
        - Records the user message and assistant reply in the database.
        - Creates a new OpenAI thread if one doesn't exist.
        - Resets context.user_data["mode"] to None.
    """
    context.user_data["mode"] = None

    intro = await load_message("random")
    image_bytes = await load_image("random")
    menu_commands = await load_menu("random")

    openai_client: OpenAIClient = context.bot_data["openai_client"]
    thread_repository: GptThreadRepository = context.bot_data["thread_repository"]

    tg_user_id = update.effective_user.id
    mode = SessionMode.RANDOM.value

    thread_id = await thread_repository.get_thread_id(tg_user_id, mode)

    if thread_id is None:
        thread = await openai_client.create_thread()
        thread_id = thread.id
        await thread_repository.create_thread(tg_user_id, mode, thread_id)

    user_message = "Give me a random interesting technical fact."

    await thread_repository.add_message(thread_id, role=MessageRole.USER.value, content=user_message)

    assistant_id = config.ai_assistant_random_facts_id

    try:
        reply = await openai_client.ask(
            assistant_id=assistant_id,
            thread_id=thread_id,
            user_message=user_message
        )
    except OpenAIError as e:
        logger.warning(f"Assistant failed in /random: {e}")
        await update.message.reply_text("Assistant failed to respond. Please try again later.")
        return

    await thread_repository.add_message(thread_id, role=MessageRole.ASSISTANT.value, content=reply)

    combined = f"{intro}\n\n{reply}"

    await send_image_bytes(
        update=update,
        context=context,
        image_bytes=image_bytes,
    )

    await send_html_message(
        update=update,
        context=context,
        text=combined,
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Use the button below to return to the main menu:",
        reply_markup=get_menu_buttons(menu_commands)
    )


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /gpt command and prepares the bot for GPT chat mode.

    Sends the introductory message and image for GPT mode and activates it for the user.
    This enables the user to start chatting with the short-response assistant.

    Args:
        update (telegram.Update): The incoming update from the Telegram user.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Context object containing bot and user data.

    Side Effects:
        - Sends the GPT welcome image and message.
        - Displays GPT-specific menu buttons.
        - Sets context.user_data["mode"] to SessionMode.GPT.
    """
    intro = await load_message("gpt")
    image_bytes = await load_image("gpt")
    menu_commands = await load_menu("gpt")

    await send_image_bytes(update, context, image_bytes)
    await send_html_message(update, context, intro)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Now you can ask me anything 👇",
        reply_markup=get_menu_buttons(menu_commands)
    )

    context.user_data["mode"] = SessionMode.GPT.value
