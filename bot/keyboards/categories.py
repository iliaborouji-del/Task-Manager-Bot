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

def create_edit_delete_keyboard(category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ اصلاح", callback_data=f"category_edit:{category_id}"),
            InlineKeyboardButton(text="🗑️ حذف", callback_data=f"category_delete:{category_id}")],
            [InlineKeyboardButton(text="بازگشت ↪️", callback_data="categories_back")]
        ]
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