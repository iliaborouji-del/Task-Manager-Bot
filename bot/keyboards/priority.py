from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_priority_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="زیاد"),
                KeyboardButton(text="متوسط"),
                KeyboardButton(text="کم")
            ]
        ],
        resize_keyboard=True
    )
    return markup