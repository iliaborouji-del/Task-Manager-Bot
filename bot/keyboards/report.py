from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_report_ketboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="هفتگی📆"),
             KeyboardButton(text="ماهانه📆"),
             KeyboardButton(text="سالانه📆")]
        ]
    )
    return markup