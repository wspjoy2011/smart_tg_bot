from functools import wraps
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from db.enums import SessionMode


def with_clean_keyboard(func):
    """
    Decorator that clears the reply keyboard and quiz state when switching out of quiz mode.

    This decorator checks if the user was previously in QUIZ mode. If so, it sends a message
    removing the quiz keyboard and clears any stored quiz progress in context.user_data.

    Args:
        func (Callable): The async handler function to wrap.

    Returns:
        Callable: A wrapped async function with keyboard cleanup logic.

    Side Effects:
        - Sends a message to remove the reply keyboard if exiting quiz mode.
        - Clears the "quiz" key from context.user_data.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        prev_mode = context.user_data.get("mode")

        if prev_mode == SessionMode.QUIZ.value:
            if update.message:
                await update.message.reply_text(
                    text="Exiting quiz mode.",
                    reply_markup=ReplyKeyboardRemove()
                )
            context.user_data.pop("quiz", None)

        return await func(update, context, *args, **kwargs)

    return wrapper
