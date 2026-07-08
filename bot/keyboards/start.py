from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ اضافه کردن وظیفه"),
            KeyboardButton(text="📋 نمایش وظایف انجام نشده")],
            [KeyboardButton(text="📢 گزارش وظایف"),
            KeyboardButton(text="🗂️ نمایش همه وظایف")]
        ],
        resize_keyboard=True
    )
    return markup