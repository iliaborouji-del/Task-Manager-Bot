from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu_keyboard(is_admin: bool = False):
    keyboard = [
        [KeyboardButton(text="➕ اضافه کردن وظیفه"),
        KeyboardButton(text="📋 نمایش وظایف انجام نشده")],
        [KeyboardButton(text="📢 گزارش وظایف"),
        KeyboardButton(text="🗂️ نمایش همه وظایف")],
        [KeyboardButton(text="🗄️ مدیریت دسته‌ بندی‌ ها")]
    ]

    if is_admin:
        keyboard.append(
            [KeyboardButton(text="🛠️ پنل مدیریت")]
        )

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)