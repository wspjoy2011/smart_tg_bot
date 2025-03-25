from telegram import (
    Update,
    InputFile,
    BotCommand,
    BotCommandScopeChat,
    MenuButtonCommands
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def send_html_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.HTML,
    )


async def send_image_bytes(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        image_bytes: bytes,
        image_name: str = "image.jpg",
        caption: str | None = None,
        parse_mode: str = ParseMode.HTML
) -> None:
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=InputFile(image_bytes, filename=image_name),
        caption=caption,
        parse_mode=parse_mode if caption else None
    )


async def show_menu(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        commands: dict[str, str]
) -> None:
    command_list = [BotCommand(cmd, desc) for cmd, desc in commands.items()]
    chat_id = update.effective_chat.id

    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(chat_id=chat_id))
    await context.bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButtonCommands())
