from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_change_status_keyboard(task_id: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="انجام شده ✅",callback_data=f"task:{task_id}:انجام شده ✅"),
             InlineKeyboardButton(text="در حال انجام ⏳",callback_data=f"task:{task_id}:در حال انجام ⏳")],
            [InlineKeyboardButton(text="🗑️ حذف", callback_data=f"delete:{task_id}")]
        ]
    )
    return markup