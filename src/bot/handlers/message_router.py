from telegram import Update
from telegram.ext import ContextTypes

from db.enums import SessionMode
from bot.handlers.gpt_handler import gpt_message_handler
from bot.handlers.quiz_handler import handle_quiz_answer


async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Routes incoming text messages based on the user's current session mode.

    This function checks the current session mode stored in `context.user_data["mode"]`
    and forwards the incoming message to the appropriate handler:
    - GPT mode: Sends the message to the GPT message handler.
    - Quiz mode: Sends the message to the quiz answer handler.
    - Otherwise, prompts the user to select an option from the menu.

    Args:
        update (telegram.Update): The incoming update from the Telegram user.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): Context containing user and bot data.

    Side Effects:
        - Delegates message handling to another handler based on session mode.
        - Sends a prompt message to the user if no mode is active.
    """
    mode = context.user_data.get("mode")

    if mode == SessionMode.GPT.value:
        await gpt_message_handler(update, context)
    elif mode == SessionMode.QUIZ.value:
        await handle_quiz_answer(update, context)
    else:
        await update.message.reply_text(
            "Please select an option from the menu to begin."
        )
