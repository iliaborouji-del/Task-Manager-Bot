from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from datetime import datetime, timedelta
import jdatetime

from celery_app.tasks.deadline_warning import send_deadline_warning
from bot.keyboards.start import create_main_menu_keyboard
from bot.states.add_task import AddTaskStates, Deadline
from bot.keyboards.add_task import (
    create_priority_keyboard,
    create_deadline_keyboard_year,
    create_deadline_keyboard_month,
    create_deadline_keyboard_days,
    create_status_keyboard,
    create_cancel_keyboard
)
from bot.templates.add_task import (
    TITLE,
    DESCRIPTION,
    PRIORITY,
    STATUS,
    SUCCESS
)

from bot.database.connection import get_session
from bot.database.add_task import save_task

router = Router()

@router.message(StateFilter("*"), F.text == "لغو❌")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="لغو شد.", reply_markup=create_main_menu_keyboard())

@router.message(F.text == "➕ اضافه کردن وظیفه")
async def add_task_start(message: Message, state: FSMContext):
    await message.answer(TITLE, reply_markup=create_cancel_keyboard())
    await state.set_state(AddTaskStates.title)
    
@router.message(AddTaskStates.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(DESCRIPTION, reply_markup=create_cancel_keyboard())
    await state.set_state(AddTaskStates.description)
    
@router.message(AddTaskStates.description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(PRIORITY, reply_markup=create_priority_keyboard())
    await state.set_state(AddTaskStates.priority)
    
@router.message(AddTaskStates.priority)
async def get_priority(message: Message, state: FSMContext):
    if message.text not in [
        "زیاد🔴",
        "متوسط🟡",
        "کم🟢"
    ]:
        await message.answer(text="لطفا یکی از گزینه ها را وارد کنید.")
        return
    
    await state.update_data(priority=message.text)
    await state.set_state(Deadline.year)
    await message.answer(text="سال را انتخاب کنید:", reply_markup=create_deadline_keyboard_year())
    await message.answer(text="برای لغو دکمه زیر را بزنید.", reply_markup=create_cancel_keyboard())
    
@router.callback_query(Deadline.year, F.data.startswith("year:"))
async def get_year(call: CallbackQuery, state: FSMContext):
    year = int(call.data.split(":")[1])
    await state.update_data(year=year)
    
    await state.set_state(Deadline.month)
    await call.message.edit_text(text="ماه را انتخاب کنید:", reply_markup=create_deadline_keyboard_month())
    await call.answer()
    
@router.callback_query(Deadline.month, F.data.startswith("month:"))
async def get_month(call: CallbackQuery, state: FSMContext):
    month = int(call.data.split(":")[1])
    await state.update_data(month=month)
    
    data = await state.get_data()
    year = data["year"]
    
    await state.set_state(Deadline.day)
    await call.message.edit_text(text="روز را انتخاب کنید:", reply_markup=create_deadline_keyboard_days(year, month))
    await call.answer()
    
@router.callback_query(Deadline.day, F.data.startswith("day:"))
async def get_day(call: CallbackQuery, state: FSMContext):
    day = int(call.data.split(":")[1])
    await state.update_data(day=day)
    
    await state.set_state(Deadline.time)
    await call.message.answer(text="زمان را وارد کنید. مثال: 18:30", reply_markup=create_cancel_keyboard())
    await call.answer()
    
@router.message(Deadline.time)
async def get_time(message: Message, state: FSMContext):
    time_text = message.text.strip()
    
    if len(time_text) != 5 or ":" not in time_text:
        await message.answer(text="فرمت زمان باید به شکل 00:00 باشد.")
        return
    
    hour_text, minute_text = time_text.split(":")
    
    if not (hour_text.isdigit(), minute_text.isdigit()):
        await message.answer(text="ساعت و دقیقه باید عدد باشند. مثال: 18:30")
        return
    
    hour = int(hour_text)
    minute = int(minute_text)
    
    if not (0 <= hour <= 23):
        await message.answer(text="ساعت باید بین 0 تا 23 باشد.")
        return
    
    if not (0 <= minute <= 59):
        await message.answer(text="دقیقه باید بین 0 تا 59 باشد.")
        return
    
    await state.update_data(hour=hour, minute=minute)
    
    data = await state.get_data()
    
    jalali_date = jdatetime.datetime(
        year=data["year"],
        month=data["month"],
        day=data["day"],
        hour=data["hour"],
        minute=data["minute"]
    )
    
    deadline_dt = jalali_date.togregorian()
    deadline_str = deadline_dt.strftime("%Y-%m-%d  %H:%M")
    await state.update_data(deadline=deadline_str)
    
    jalali_text = f"{data['year']}/{data['month']:02d}/{data['day']:02d}  {data['hour']:02d}:{data['minute']:02d}"
    
    await message.answer(text=f"ددلاین ثبت شد:\n\n {jalali_text}")
    
    await message.answer(STATUS, reply_markup=create_status_keyboard())
    await state.set_state(AddTaskStates.status)
    
@router.message(AddTaskStates.status)
async def get_status(message: Message, state: FSMContext):
    if message.text not in [
        "انجام شده✅",
        "در حال انجام⏳",
        "انجام نشده⭕"
    ]:
        await message.answer("لطفا یکی از وضعیت ها را انتخاب کنید.")
        return
    
    await state.update_data(status=message.text)
    
    data = await state.get_data()
    session = await get_session()
    await save_task(
        session=session,
        user_id=message.from_user.id,
        data=data
    )
    
    deadline_str = data["deadline"]
    deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d  %H:%M")
    
    warning_time = deadline_dt - timedelta(days=1)
    
    send_deadline_warning.apply_async(
        args=[message.from_user.id, data["title"], deadline_str],
        eta=warning_time
    )
    
    await message.answer(SUCCESS, reply_markup=create_main_menu_keyboard())
    
    await state.clear()