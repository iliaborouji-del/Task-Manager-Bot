from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton(text="📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_back")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_users_keyboard(users, show_more: bool = False, next_offset: int = 0):

    keyboard = []

    for user in users:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{user.full_name} | {user.user_id}",
                    callback_data=f"admin_user:{user.user_id}",
                )
            ]
        )

    if show_more:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="⬇️ نمایش بیشتر",
                    callback_data=f"admin_users_more_{next_offset}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 بازگشت",
                callback_data="admin_back"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )
    
def create_user_management_keyboard(user_id: int, is_admin: bool, is_premium: bool, is_blocked: bool):
    keyboard = [
        [
            InlineKeyboardButton(
                text=(
                    "👑 حذف ادمین"
                    if is_admin
                    else "👑 ادمین کن"
                ),
                callback_data=f"user_admin:{user_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=(
                    "⭐ حذف پرمیوم"
                    if is_premium
                    else "⭐ پرمیوم کن"
                ),
                callback_data=f"user_premium:{user_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text=(
                    "✅ رفع مسدودی"
                    if is_blocked
                    else "🚫 مسدود کن"
                ),
                callback_data=f"user_block:{user_id}",
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 بازگشت",
                callback_data="admin_users",
            )
        ]
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )