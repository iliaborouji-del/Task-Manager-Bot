from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
import jdatetime

months = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند"
]

def create_deadline_keyboard_year():
    builder = InlineKeyboardBuilder()
    
    for year in range(1405, 1409):
        builder.button(
            text=str(year),
            callback_data=f"year:{year}"
        )
        
    builder.adjust(2)
    return builder.as_markup()

def create_deadline_keyboard_month():
    builder = InlineKeyboardBuilder()
    
    for i, month in enumerate(months, start=1):
        builder.button(
            text=str(month),
            callback_data=f"month:{i}"
        )
        
    builder.adjust(3)
    return builder.as_markup()

def days(year: int, month: int) -> int:
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    
    return 30 if jdatetime.date(year, 1, 1).isleap() else 29

def create_deadline_keyboard_days(year: int, month: int):
    builder = InlineKeyboardBuilder()
    
    days = days(year, month)
    
    for day in range(1, days + 1):
        builder.button(
            text=f"{day:02}",
            callback_data=f"day:{day}"
        )
        
    builder.adjust(7)
    return builder.as_markup()