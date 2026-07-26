from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

def create_categories_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ اضافه کردن دسته‌بندی"),
            KeyboardButton(text="✏️ اصلاح یا حذف دسته‌بندی")],
            [KeyboardButton(text="بازگشت ↪️")]
        ],
        resize_keyboard=True,
    )

def create_edit_delete_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✏️ اصلاح"),
                KeyboardButton(text="🗑️ حذف"),
            ],
            [
                KeyboardButton(text="بازگشت ↪️"),
            ],
        ],
        resize_keyboard=True,
    )

def create_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = []

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"category_select:{category.id}",
                )
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="بازگشت ↪️",
                callback_data="categories_back",
            )
        ]
    )
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_show_tasks_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = []

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"show_tasks_category:{category.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="بازگشت ↪️",
                callback_data="show_tasks_back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_show_all_tasks_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = []

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"show_all_tasks_category:{category.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="بازگشت ↪️",
                callback_data="show_all_tasks_back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_move_tasks_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = []

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=category.name,
                    callback_data=f"move_category:{category.id}",
                )
            ]
        )
        
    keyboard.append(
        [
            InlineKeyboardButton(
                text="بازگشت ↪️",
                callback_data="categories_back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_task_categories_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = []

    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📁 {category.name}",
                    callback_data=f"task_category:{category.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="➕ اضافه کردن دسته‌بندی",
                callback_data="task_category:new",
            )
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="بازگشت ↪️",
                callback_data="task_category:back",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_category_cancel_keyboard():
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="لغو ❌")]
        ],
        resize_keyboard=True
    )
    return markup