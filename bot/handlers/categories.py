from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database.connection import session_scope
from bot.keyboards.start import create_main_menu_keyboard
from bot.database.categories import (
    create_category,
    category_exists,
    get_all_categories,
)
from bot.keyboards.categories import (
    create_categories_menu,
    create_categories_keyboard,
    create_category_cancel_keyboard,
    create_edit_delete_reply_keyboard,
    create_move_tasks_keyboard,
)
from bot.states.categories import CategoriesStates
from bot.database.categories import (
    rename_category,
    get_category,
)
from bot.database.categories import (
    delete_category,
    move_tasks_to_category,
    category_has_tasks,
    get_other_categories,
)

router = Router()

@router.message(F.text == "🗄️ مدیریت دسته‌ بندی‌ ها")
async def categories_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text="یکی از گزینه‌های زیر را انتخاب کنید.",
        reply_markup=create_categories_menu(),
    )
    
    await state.set_state(CategoriesStates.wating_for_choose)
    


@router.message(F.text == "➕ اضافه کردن دسته‌بندی")
async def add_category(message: Message, state: FSMContext):
    await message.answer(
        text="نام دسته‌بندی جدید را وارد کنید:",
        reply_markup=create_category_cancel_keyboard()
    )
    await state.set_state(CategoriesStates.waiting_for_category_name)
    
@router.message(
    CategoriesStates.waiting_for_category_name,
    F.text == "❌ لغو"
)
async def cancel_categories(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text="لغو شد.",
        reply_markup=create_categories_menu(),
    )
    await state.set_state(CategoriesStates.wating_for_choose)

@router.message(CategoriesStates.waiting_for_category_name)
async def save_category(message: Message, state: FSMContext):
    name = message.text.strip()

    if not name:
        await message.answer(text="نام دسته‌بندی نمی‌تواند خالی باشد.")
        return

    async with session_scope() as session:

        exists = await category_exists(
            session=session,
            user_id=message.from_user.id,
            name=name,
        )

        if exists:
            await message.answer(text="این دسته‌بندی قبلاً ایجاد شده است.")
            return

        await create_category(
            session=session,
            user_id=message.from_user.id,
            name=name,
        )

    await message.answer(
        text="✅ دسته‌بندی با موفقیت ایجاد شد.",
        reply_markup=create_categories_menu(),
    )
    await state.set_state(CategoriesStates.wating_for_choose)

@router.message(F.text == "✏️ اصلاح یا حذف دسته‌بندی")
async def show_categories(message: Message):
    async with session_scope() as session:
        categories = await get_all_categories(
            session=session,
            user_id=message.from_user.id,
        )

    if not categories:
        await message.answer(text="هنوز هیچ دسته‌بندی ایجاد نکرده‌اید.")
        return

    await message.answer(
        text="دسته‌بندی موردنظر را انتخاب کنید:",
        reply_markup=create_categories_keyboard(categories)
    )

@router.callback_query(F.data.startswith("category_select:"))
async def select_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])

    await state.update_data(category_id=category_id)
    
    await state.set_state(CategoriesStates.selected_category)

    await call.message.delete()

    await call.message.answer(
        text="عملیات موردنظر را انتخاب کنید:",
        reply_markup=create_edit_delete_reply_keyboard(),
    )

    await call.answer()

@router.message(CategoriesStates.selected_category, F.text == "✏️ اصلاح")
async def edit_category(message: Message, state: FSMContext):
    await message.answer(text="نام جدید دسته‌بندی را وارد کنید:")

    await state.set_state(
        CategoriesStates.waiting_for_new_category_name
    )

@router.message(CategoriesStates.waiting_for_new_category_name)
async def save_new_category_name(message: Message, state: FSMContext):
    new_name = message.text.strip()

    if not new_name:
        await message.answer(text="نام دسته‌بندی نمی‌تواند خالی باشد.")
        return

    data = await state.get_data()

    category_id = data["category_id"]

    async with session_scope() as session:
        exists = await category_exists(
            session=session,
            user_id=message.from_user.id,
            name=new_name,
        )

        if exists:
            await message.answer(text="دسته‌بندی دیگری با این نام وجود دارد.")
            return

        category = await get_category(
            session=session,
            category_id=category_id,
            user_id=message.from_user.id,
        )

        if category is None:
            await state.clear()
            await message.answer(
                text="دسته‌بندی پیدا نشد.",
                reply_markup=create_categories_menu(),
            )
            return

        await rename_category(
            session=session,
            category_id=category_id,
            user_id=message.from_user.id,
            new_name=new_name,
        )

    await message.answer(
        text="✅ نام دسته‌بندی با موفقیت تغییر کرد.",
        reply_markup=create_categories_menu(),
    )
    await state.set_state(CategoriesStates.wating_for_choose)
    
@router.message(CategoriesStates.selected_category, F.text == "بازگشت ↪️")
async def back_to_categories(message: Message, state: FSMContext):
    await state.clear()

    async with session_scope() as session:
        categories = await get_all_categories(
            session=session,
            user_id=message.from_user.id,
        )

    if not categories:
        await message.answer(
            text="هنوز هیچ دسته‌بندی ایجاد نکرده‌اید.",
            reply_markup=create_categories_menu(),
        )
        return

    await message.answer(
        text="دسته‌بندی موردنظر را انتخاب کنید:",
        reply_markup=create_categories_keyboard(categories),
    )
    
@router.callback_query(F.data == "categories_back")
async def categories_back(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    await call.message.answer(
        text="مدیریت دسته ‌بندی‌ ها",
        reply_markup=create_categories_menu(),
    )
    await state.set_state(CategoriesStates.wating_for_choose)
    await call.answer()

@router.message(CategoriesStates.selected_category, F.text == "🗑️ حذف")
async def delete_category_start(message: Message, state: FSMContext):
    data = await state.get_data()

    category_id = data["category_id"]

    async with session_scope() as session:
        has_tasks = await category_has_tasks(
            session=session,
            category_id=category_id,
            user_id=message.from_user.id,
        )

        if not has_tasks:
            await delete_category(
                session=session,
                category_id=category_id,
                user_id=message.from_user.id,
            )
            await message.answer(
                "✅ دسته‌بندی حذف شد."
            )
            return

        categories = await get_other_categories(
            session=session,
            user_id=message.from_user.id,
            category_id=category_id,
        )

    if not categories:
        await message.answer(
            text="این دسته‌بندی دارای وظیفه است.\n\n"
                 "ابتدا یک دسته‌بندی دیگر ایجاد کنید."
        )
        return

    await state.update_data(source_category_id=category_id)

    

    await message.answer(
        text="این دسته‌بندی دارای وظیفه است.\n\n"
             "وظایف را به کدام دسته‌بندی منتقل کنم؟",
        reply_markup=create_move_tasks_keyboard(categories)
    )

    await state.set_state(CategoriesStates.waiting_for_move_category)

@router.callback_query(CategoriesStates.waiting_for_move_category, F.data.startswith("move_category:"))
async def move_tasks(call: CallbackQuery, state: FSMContext):
    destination_category = int(call.data.split(":")[1])

    data = await state.get_data()

    source_category = data["source_category_id"]

    async with session_scope() as session:
        await move_tasks_to_category(
            session=session,
            old_category_id=source_category,
            new_category_id=destination_category,
            user_id=call.from_user.id,
        )

        await delete_category(
            session=session,
            category_id=source_category,
            user_id=call.from_user.id,
        )

    await state.clear()

    await call.message.edit_text(text="✅ تمام وظایف منتقل شدند و دسته‌بندی حذف شد.", reply_markup=create_edit_delete_reply_keyboard())

    await call.answer()
       
@router.message(CategoriesStates.wating_for_choose, F.text == "بازگشت ↪️")
async def return_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="منوی اصلی", reply_markup=create_main_menu_keyboard())

