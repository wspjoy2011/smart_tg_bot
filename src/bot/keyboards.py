from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_menu_buttons(buttons: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=label, callback_data=command)]
        for command, label in buttons.items()
    ])
