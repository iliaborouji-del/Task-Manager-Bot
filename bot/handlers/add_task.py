from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import jdatetime

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
    
router.callback_query(StateFilter("*"), F.data == "cancel")
async def cancel_2(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(text="لغو شد.", reply_markup=create_main_menu_keyboard())
    await call.answer()

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
    
    await state.set_state(Deadline.hour)
    await call.message.answer(text="ساعت را وارد کنید(مثال:18):", reply_markup=create_cancel_keyboard())
    await call.answer()
    
@router.message(Deadline.hour)
async def get_hour(message: Message, state: FSMContext):
    try:
        hour = int(message.text)
        if not (0 <= hour <= 23):
            raise ValueError
    except:
        await message.answer(text="ساعت باید بین 0 تا 23 باشد.")
        return
    
    await state.update_data(hour=hour)
    await state.set_state(Deadline.minute)
    await message.answer(text="دقیقه را وارد کنید(مثال: 05):", reply_markup=create_cancel_keyboard())
    
@router.message(Deadline.minute)
async def get_minute(message: Message, state: FSMContext):
    try: 
        minute = int(message.text)
        if not (0 <= minute <= 59):
            raise ValueError
    except:
        await message.answer("دقیقه باید بین 0 تا 59 باشد.")
        return
    
    await state.update_data(minute=minute)
    
    data = await state.get_data()
    
    jalali_date = jdatetime.datetime(
        year=data["year"],
        month=data["month"],
        day=data["day"],
        hour=data["hour"],
        minute=data["minute"]
    )
    
    deadline_dt = jalali_date.togregorian()
    deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M")
    await state.update_data(deadline=deadline_str)
    
    jalali_text = f"{data['year']}/{data['month']}/{data['day']}  {data['hour']}:{data['minute']}"
    
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
    
    await message.answer(SUCCESS, reply_markup=create_main_menu_keyboard())
    
    await state.clear()