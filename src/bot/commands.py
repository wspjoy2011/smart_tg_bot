from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards import get_main_menu_button
from bot.message_sender import send_html_message, send_image_bytes, show_menu
from bot.resource_loader import load_message, load_image, load_menu, load_prompt
from db.repository import GptSessionRepository
from services import OpenAIClient


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    prompt = await load_prompt("random")
    intro = await load_message("random")
    image_bytes = await load_image("random")

    openai_client: OpenAIClient = context.bot_data["openai_client"]
    session_repository: GptSessionRepository = context.bot_data["session_repository"]

    reply = await openai_client.ask(
        user_message="Give me a random interesting technical fact.",
        system_prompt=prompt
    )

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
        reply_markup=get_main_menu_button()
    )
