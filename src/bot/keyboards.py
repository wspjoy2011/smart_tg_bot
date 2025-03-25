from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Main Menu", callback_data="start")]
    ])
