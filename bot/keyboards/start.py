from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ اضافه کردن وظیفه"),
            KeyboardButton(text="📋 نمایش وظیفه‌ها")],
            [KeyboardButton(text="گزارش وظایف 📢")]
        ],
        resize_keyboard=True
    )
    return markup