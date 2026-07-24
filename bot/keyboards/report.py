from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def create_report_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="هفتگی 📆"),
             KeyboardButton(text="ماهانه 📆"),
             KeyboardButton(text="سالانه 📆")],
            [KeyboardButton(text="بازگشت ↪️")]
        ],
        resize_keyboard=True
    )
    return markup

def create_report_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="📂 همه دسته‌بندی‌ها",
                callback_data="report_category:all",
            )
        ]
    ]

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📁 {category.name}",
                    callback_data=f"report_category:{category.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="بازگشت ↪️",
                callback_data="report_back",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )