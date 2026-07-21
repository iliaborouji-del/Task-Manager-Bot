from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_change_status_keyboard(task_id: int, second_status: str):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="انجام شده ✅",callback_data=f"task:{task_id}:انجام شده ✅"),
             InlineKeyboardButton(text=second_status,callback_data=f"task:{task_id}:{second_status}")],
            [InlineKeyboardButton(text="🗑️ حذف", callback_data=f"delete:{task_id}"), 
             InlineKeyboardButton(text="📷 نمایش QR Code", callback_data=f"qr:{task_id}")]
        ]
    )
    return markup

def create_delete_keyboard(task_id: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ حذف", callback_data=f"delete:{task_id}")]
        ]
    )
    return markup