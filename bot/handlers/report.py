import jdatetime
from datetime import timezone, timedelta
from aiogram.filters import StateFilter
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.report import create_report_keyboard
from bot.keyboards.start import create_main_menu_keyboard
from bot.database.connection import session_scope
from bot.states.report import ReportState
from bot.database.report import (
    get_total_tasks,
    get_overdue_tasks,
    get_completed_tasks,
    get_date_range,
    get_idle_days,
    get_most_active_days,
    get_in_progress_tasks,
    get_next_deadline,
    get_not_done_tasks,
    calc_on_time,
    calc_completion_rate
)

router = Router()

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

@router.message(StateFilter("*"), F.text == "بازگشت ↪️")
async def return_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="منوی اصلی", reply_markup=create_main_menu_keyboard())

@router.message(F.text == "📢 گزارش وظایف")
async def report_message(message: Message, state: FSMContext):
    await message.answer(text="بازه زمانی را مشخص کنید:", reply_markup=create_report_keyboard())
    await state.set_state(ReportState.waiting_for_date_range)
    
@router.message(ReportState.waiting_for_date_range)
async def show_report(message: Message, state: FSMContext):
    async with session_scope() as session:
        if message.text == "هفتگی 📆":
            report_type = "weekly"
        elif message.text == "ماهانه 📆":
            report_type = "monthly"
        elif message.text == "سالانه 📆":
            report_type = "yearly"
        else:
            await message.answer(text="لطفا یکی از گزینه ها را انتخاب کنید.")
            return
            
        start, end = get_date_range(report_type)
        
        user_id = message.from_user.id
        
        total_tasks = await get_total_tasks(session, user_id, start, end)
        completed_tasks = await get_completed_tasks(session, user_id, start, end)
        doing_tasks = await get_in_progress_tasks(session, user_id, start, end)
        not_done_tasks = await get_not_done_tasks(session, user_id, start, end)
        overdue_tasks = await get_overdue_tasks(session, user_id, start, end)
        
        completion_rate = calc_completion_rate(len(total_tasks), len(completed_tasks))
        on_time = calc_on_time(completed_tasks)
        
        active_day, active_count = await get_most_active_days(session, user_id, start, end)
        next_deadline = await get_next_deadline(session, user_id)
        
        active_date = [task.created_at.date() for task in total_tasks]
        idle_days_count = get_idle_days(start, end, active_date)
        
        if active_day:
            jalali_active = jdatetime.date.fromgregorian(date=active_day)
            active_day_text = "\u200E" + jalali_active.strftime("%Y/%m/%d")
        else:
            active_day_text = "_"
            
        if next_deadline:
            try:
                deadline = next_deadline.deadline.astimezone(IRAN_TZ)

                jalali_deadline = jdatetime.datetime.fromgregorian(datetime=deadline)

                next_deadline_text = jalali_deadline.strftime("%Y/%m/%d  %H:%M")

            except Exception:
                next_deadline_text = "فرمت ددلاین نامعتبر است."
        else:
            next_deadline_text = "_"
            
        text = (
            "----------\n" + "\u200E"
            f"📋 مجموع وظایف: {len(total_tasks)}\n"
            f"✅ انجام شده: {len(completed_tasks)}\n"
            f"⏳ در حال انجام: {len(doing_tasks)}\n"
            f"⭕ انجام نشده: {len(not_done_tasks)}\n"
            f"⌛ عقب افتاده: {len(overdue_tasks)}\n"
            "----------\n" + "\u200E"
            f"📈 نرخ تکمیل: {completion_rate}%\n"
            f"⏰ انجام به موقع: {on_time}%\n"
            f"🔥 فعال ترین روز: {active_day_text} ({active_count} وظیفه)\n"
            f"😴 روز های بدون فعالیت: {idle_days_count}\n"
            f"⚠️ نزدیک ترین ددلاین: {next_deadline_text}\n"
            "----------\n" + "\u200E"
            "ادامه دهید 💪"
        )
        
        await message.answer(text=text)
        await state.clear()