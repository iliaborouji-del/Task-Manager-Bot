from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_delete_keyboard(task_id: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑️ حذف وظیفه", callback_data=f"delete:{task_id}")]
        ]
    )
    return markup