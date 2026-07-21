from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_qr_keyboard(task_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📷 نمایش QR Code", callback_data=f"qr:{task_id}")]
        ]
    )
    return markup