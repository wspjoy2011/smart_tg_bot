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
    """
    Sends an HTML-formatted message to the current chat.

    Args:
        update (Update): Telegram update containing chat context.
        context (ContextTypes.DEFAULT_TYPE): Telegram context for bot interaction.
        text (str): HTML-formatted text to send.
    """
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
    """
    Sends an image from bytes to the current chat with optional caption.

    Args:
        update (Update): Telegram update containing chat context.
        context (ContextTypes.DEFAULT_TYPE): Telegram context for bot interaction.
        image_bytes (bytes): Byte data of the image to send.
        image_name (str, optional): Filename for the image. Defaults to "image.jpg".
        caption (str, optional): Optional caption to include with the image.
        parse_mode (str, optional): Parsing mode for caption formatting. Defaults to HTML.
    """
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
    """
    Sets a custom menu of commands for the current chat session.

    Args:
        update (Update): Telegram update containing chat context.
        context (ContextTypes.DEFAULT_TYPE): Telegram context for bot interaction.
        commands (dict[str, str]): Dictionary where keys are command names
            and values are their descriptions.
    """

    command_list = [BotCommand(cmd, desc) for cmd, desc in commands.items()]
    chat_id = update.effective_chat.id

    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(chat_id=chat_id))
    await context.bot.set_chat_menu_button(chat_id=chat_id, menu_button=MenuButtonCommands())
