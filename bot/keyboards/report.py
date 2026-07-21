from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_report_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="هفتگی 📆"),
             KeyboardButton(text="ماهانه 📆"),
             KeyboardButton(text="سالانه 📆")],
            [KeyboardButton(text="بازگشت ↪️")]
        ],
        resize_keyboard=True
    )
    return markup