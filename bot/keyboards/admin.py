from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton(text="📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_users_keyboard(show_more: bool = False, next_offset: int = 0):
    keyboard = []

    if show_more:
        keyboard.append(
            [InlineKeyboardButton(text="⬇️ نمایش بیشتر", callback_data=f"admin_users_more_{next_offset}")]
        )

    keyboard.append(
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )