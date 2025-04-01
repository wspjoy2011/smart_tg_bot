from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
