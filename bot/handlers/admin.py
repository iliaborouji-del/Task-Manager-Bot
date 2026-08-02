from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.filters.admin import AdminFilter
from bot.keyboards.admin import (
    create_admin_keyboard,
    create_users_keyboard,
    create_user_management_keyboard
)
from bot.database.connection import session_scope
from bot.utils.datetime import jalali_string
from bot.database.admin import (
    get_users_count,
    get_users_page,
    get_tasks_count,
    get_categories_count,
    get_active_users_count,
    get_new_users_today_count,
    get_blocked_users_count,
    get_last_registered_user,
    get_all_users_ids,
    get_user_by_id,
    toggle_admin,
    toggle_premium,
    toggle_block,
    refresh_user
)
from bot.states.admin import AdminStates

router = Router()

async def build_stats_text(
    total_users: int,
    active_users: int,
    new_users: int,
    blocked_users: int,
    tasks_count: int,
    categories_count: int,
    last_user,
):
    text = (
        "\u200F━━━━━━━━━━━━━━━━━━\n"
        "📊 آمار ربات\n"
        "\u200F━━━━━━━━━━━━━━━━━━\n"
        "👥 کاربران:\n"
        f"• تعداد کل کاربران: {total_users}\n"
        f"• کاربران فعال ۷ روز اخیر: {active_users}\n"
        f"• کاربران جدید امروز: {new_users}\n"
        f"• کاربران مسدود شده: {blocked_users}\n"
        "\u200F━━━━━━━━━━━━━━━━━━\n"
        "📝 وظایف:\n"
        f"• تعداد کل وظایف: {tasks_count}\n"
        "\u200F━━━━━━━━━━━━━━━━━━\n"
        "📂 دسته‌بندی‌ها:\n"
        f"• تعداد دسته‌بندی‌ها: {categories_count}\n"
    )

    if last_user:
        created = jalali_string(
            last_user.created_at
        )

        text += (
            "\u200F━━━━━━━━━━━━━━━━━━\n"
            "🆕 آخرین ثبت‌نام:\n"
            f"👤 نام: {last_user.full_name}\n"
            f"🆔 شناسه: \u200E{last_user.user_id}\n"
            f"📅 تاریخ عضویت: \u200E{created}\n"
        )

    text += (
        "\u200F━━━━━━━━━━━━━━━━━━"
    )

    return text

async def build_users_text(users, total_count: int, offset: int):
    text = (
        "\u200F━━━━━━━━━━━━━━━━━━\n"
        "👥 مدیریت کاربران\n"
        f"👤 تعداد کل کاربران: {total_count}\n"
        "\u200F━━━━━━━━━━━━━━━━━━\n"
    )

    for index, user in enumerate(users, start=offset + 1):
        created = jalali_string(user.created_at)
        username = (
            f"@{user.username}"
            if user.username
            else "ندارد"
        )

        status = (
            "🚫 مسدود"
            if user.is_blocked
            else "✅ فعال"
        )

        text += (
            f"\u200F🔹 کاربر شماره {index}\n"
            f"🆔 شناسه: \u200E{user.user_id}\n"
            f"👤 نام: {user.full_name}\n"
            f"📱 نام کاربری: {username}\n"
            f"📅 تاریخ عضویت: \u200E{created}\n"
            f"📌 وضعیت: {status}\n"
            "\u200F━━━━━━━━━━━━━━━━━━\n"
        )

    return text


async def show_users(call: CallbackQuery, offset: int = 0):
    async with session_scope() as session:
        limit = 10
        total_count = await get_users_count(session)
        users = await get_users_page(
            session=session,
            offset=offset,
            limit=limit,
        )

        text = await build_users_text(
            users=users,
            total_count=total_count,
            offset=offset
        )
        show_more = (
            offset + limit < total_count
        )
        await call.message.edit_text(
            text,
            reply_markup=create_users_keyboard(
                users=users,
                show_more=show_more,
                next_offset=offset + limit
            )
        )

@router.message(Command("admin"), AdminFilter())
async def admin_panel(message: Message):
    await message.answer(
        "🛠️ پنل مدیریت",
        reply_markup=create_admin_keyboard()
    )

@router.callback_query(F.data == "admin_users", AdminFilter())
async def admin_users(call: CallbackQuery):
    await call.answer()
    await show_users(call=call)

@router.callback_query(F.data.startswith("admin_users_more_"), AdminFilter())
async def admin_users_more(call: CallbackQuery):
    await call.answer()

    offset = int(
        call.data.split("_")[-1]
    )

    await show_users(
        call=call,
        offset=offset,
    )

@router.callback_query(F.data == "admin_stats", AdminFilter())
async def admin_stats(call: CallbackQuery):
    await call.answer()
    async with session_scope() as session:
        total_users = await get_users_count(session)
        active_users = await get_active_users_count(session)
        new_users = await get_new_users_today_count(session)
        blocked_users = await get_blocked_users_count(session)
        tasks_count = await get_tasks_count(session)
        categories_count = await get_categories_count(session)
        last_user = await get_last_registered_user(session)

    text = await build_stats_text(
        total_users=total_users,
        active_users=active_users,
        new_users=new_users,
        blocked_users=blocked_users,
        tasks_count=tasks_count,
        categories_count=categories_count,
        last_user=last_user,
    )

    await call.message.edit_text(
        text,
        reply_markup=create_admin_keyboard()
    )

@router.callback_query(F.data == "admin_broadcast", AdminFilter())
async def admin_broadcast(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await state.set_state(
        AdminStates.waiting_for_broadcast
    )

    await call.message.edit_text(
        text="📢 ارسال همگانی\n\n"
            "لطفاً پیام مورد نظر برای ارسال را ارسال کنید."
    )
    
@router.message(AdminStates.waiting_for_broadcast, AdminFilter())
async def send_broadcast(message: Message, state: FSMContext,):
    async with session_scope() as session:
        users_ids = await get_all_users_ids(
            session
        )

    success = 0
    failed = 0
    for user_id in users_ids:
        try:
            await message.bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            success += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        text="📢 گزارش ارسال همگانی\n\n"
            f"✅ موفق: {success}\n"
            f"❌ ناموفق: {failed}",
        reply_markup=create_admin_keyboard()
    )

@router.callback_query(F.data == "admin_back", AdminFilter())
async def admin_back(call: CallbackQuery):
    await call.answer()

    await call.message.edit_text(
        text="🛠️ پنل مدیریت",
        reply_markup=create_admin_keyboard()
    )
    
@router.callback_query(F.data.startswith("admin_user:"), AdminFilter())
async def admin_user_detail(call: CallbackQuery):
    await call.answer()

    user_id = int(
        call.data.split(":")[1]
    )

    async with session_scope() as session:

        user = await get_user_by_id(
            session=session,
            user_id=user_id,
        )

    if user is None:
        await call.message.edit_text(
            "کاربر پیدا نشد."
        )
        return

    text = (
        "👤 اطلاعات کاربر\n\n"
        f"🆔 شناسه: {user.user_id}\n"
        f"نام: {user.full_name}\n"
        f"ادمین: {'✅' if user.is_admin else '❌'}\n"
        f"پرمیوم: {'⭐' if user.is_premium else '❌'}\n"
        f"مسدود: {'🚫' if user.is_blocked else '✅'}"
    )

    await call.message.edit_text(
        text=text,
        reply_markup=create_user_management_keyboard(
            user_id=user.user_id,
            is_admin=user.is_admin,
            is_premium=user.is_premium,
            is_blocked=user.is_blocked,
        )
    )
    
@router.callback_query(F.data.startswith("user_admin:"), AdminFilter())
async def change_user_admin(call: CallbackQuery):
    await call.answer()

    user_id = int(
        call.data.split(":")[1]
    )

    async with session_scope() as session:

        user = await refresh_user(
            session=session,
            user_id=user_id,
        )

        if user is None:
            await call.answer(
                "کاربر پیدا نشد.",
                show_alert=True
            )
            return

        await toggle_admin(
            session=session,
            user=user,
        )

        user = await refresh_user(
            session=session,
            user_id=user_id,
        )

    await call.message.edit_reply_markup(
        reply_markup=create_user_management_keyboard(
            user_id=user.user_id,
            is_admin=user.is_admin,
            is_premium=user.is_premium,
            is_blocked=user.is_blocked,
        )
    )
    
@router.callback_query(F.data.startswith("user_block:"), AdminFilter())
async def change_user_block(call: CallbackQuery):
    await call.answer()

    user_id = int(
        call.data.split(":")[1]
    )

    async with session_scope() as session:

        user = await refresh_user(
            session=session,
            user_id=user_id,
        )

        if user is None:
            return

        await toggle_block(
            session=session,
            user=user,
        )

        user = await refresh_user(
            session=session,
            user_id=user_id,
        )

    await call.message.edit_reply_markup(
        reply_markup=create_user_management_keyboard(
            user_id=user.user_id,
            is_admin=user.is_admin,
            is_premium=user.is_premium,
            is_blocked=user.is_blocked,
        )
    )