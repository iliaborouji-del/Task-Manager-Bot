from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_status_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="انجام شده✅"),
                KeyboardButton(text="در حال انجام⏳"),
                KeyboardButton(text="انجام نشده❌")
            ]
        ],
        resize_keyboard=True
    )
    return markup