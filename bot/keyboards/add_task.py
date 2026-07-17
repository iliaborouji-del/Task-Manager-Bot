from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import jdatetime

#----------priority----------
def create_priority_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
                [KeyboardButton(text="زیاد 🔴"),
                KeyboardButton(text="متوسط 🟡"),
                KeyboardButton(text="کم 🟢")],
                [KeyboardButton(text="لغو ❌")]
        ],
        resize_keyboard=True
    )
    return markup

#-----------deadline----------
def create_deadline_keyboard_year() -> InlineKeyboardMarkup:
    yaers = [1405, 1406, 1407, 1408]
    
    keyboard = []
    row = []
    
    for year in yaers:
        row.append(
            InlineKeyboardButton(
                text=str(year),
                callback_data=f"year:{year}"
            )
        )
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_deadline_keyboard_month() -> InlineKeyboardMarkup:
    months = [
        "فروردین","اردیبهشت","خرداد",
        "تیر","مرداد","شهریور",
        "مهر","آبان","آذر",
        "دی","بهمن","اسفند"
    ]
    
    keyboard = []
    row = []
    
    for i, name in enumerate(months, start=1):
        row.append(
            InlineKeyboardButton(
                text=name,
                callback_data=f"month:{i}"
            )
        )
        
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_days(year: int, month: int) -> int:
    if month in [1,2,3,4,5,6]:
        return 31
    if month in [7,8,9,10,11]:
        return 30
    if month == 12:
        try:
            jdatetime.date(year, 12, 30)
            return 30
        except:
            return 29

def create_deadline_keyboard_days(year: int, month: int) -> InlineKeyboardMarkup:
    days = get_days(year, month)
    
    keyboard = []
    row = []
    
    for day in range(1, days + 1):
        row.append(
            InlineKeyboardButton(
                text=str(day),
                callback_data=f"day:{day}"
            )
        )
        
        if len(row) == 7:
            keyboard.append(row)
            row = []
            
    if row:
        while len(row) < 7:
            row.append(
                InlineKeyboardButton(
                    text=" ",
                    callback_data="ignore"
                )
            )
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

#----------status----------
def create_status_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="انجام شده ✅"),
                KeyboardButton(text="در حال انجام ⏳"),
                KeyboardButton(text="انجام نشده ⭕")
            ],
            [KeyboardButton(text="لغو ❌")]
        ],
        resize_keyboard=True
    )
    return markup

#----------cancel---------
def create_cancel_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="لغو ❌")]
        ]
    )
    return markup