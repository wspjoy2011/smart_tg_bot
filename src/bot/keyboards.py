from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)


def get_menu_buttons(buttons: dict[str, str]) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard markup from a dictionary of button commands and labels.

    Args:
        buttons (dict[str, str]): A dictionary where keys are callback data (commands),
            and values are button labels to display.

    Returns:
        InlineKeyboardMarkup: Telegram markup object containing the buttons.
    """

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=label, callback_data=command)]
        for command, label in buttons.items()
    ])


def get_quiz_answer_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    """
    Creates a reply keyboard markup for quiz answer options.

    Args:
        options (list[str]): A list of possible answer options (e.g. "A", "B", "C", "D").

    Returns:
        ReplyKeyboardMarkup: Telegram markup object with quiz answer buttons.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(option)] for option in options],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Choose your answer"
    )
