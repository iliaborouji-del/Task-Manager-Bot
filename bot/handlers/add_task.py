from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from datetime import datetime
import jdatetime

from bot.states.add_task import AddTaskStates
from bot.keyboards.priority import create_priority_keyboard
from bot.keyboards.deadline import (
    create_deadline_keyboard_days,
    create_deadline_keyboard_month,
    create_deadline_keyboard_year
)
from bot.templates.add_task import (
    TITLE,
    DESCRIPTION,
    PRIORITY,
    DEADLINE,
    STATUS,
    SUCCESS
)

from bot.database.connection import get_session
from bot.database.add_task import save_task

router = Router()

@router.message(F.text == "➕ اضافه کردن وظیفه")
async def add_task_start(message: Message, state: FSMContext):
    await message.answer(TITLE)
    await state.set_state(AddTaskStates.title)
    
@router.message(AddTaskStates.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(DESCRIPTION)
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
    await message.answer(text="سال را انتخاب کنید:", reply_markup=create_deadline_keyboard_year())
    await state.set_state(AddTaskStates.deadline)
    
@router.callback_query(AddTaskStates.deadline, F.data.startswith("year:"))
async def get_year(call: CallbackQuery, state: FSMContext):
    year = int(call.data.split(":")[1])

    await state.update_data(year=year)
    
    await call.message.answer(text="ماه را انتخاب کنید:", reply_markup=create_deadline_keyboard_month())
    
    await call.answer()
    
@router.callback_query(AddTaskStates.deadline, F.data.startswith("month:"))
async def get_month(call: CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    
    year = data["year"]
    
    month = int(call.data.split(":")[1])
    
    await state.update_data(month=month)
    
    await call.message.answer(text="روز را انتخاب کنید:", reply_markup=create_deadline_keyboard_days(year, month))
    
    await call.answer()
    
@router.message(AddTaskStates.deadline, F.data.startswith("day:"))
async def get_year(message: Message, state: FSMContext, call: CallbackQuery):
    day = int(call.data.split(":")[1])
    
    await state.update_data(day=day)
    
    data = await state.get_data()
    
    jalali_date = jdatetime.datetime(
        year=data["year"],
        month=data["month"],
        day=data["day"]
    )
    
    deadline = jalali_date.togregorian()
    
    await message.answer(text=deadline)
    
    await state.update_data(deadline=deadline)
    await message.answer(STATUS)
    await state.set_state(AddTaskStates.status)
    
@router.message(AddTaskStates.status)
async def get_status(message: Message, state: FSMContext):
    if message.text not in [
        "انجام شده",
        "در حال انجام",
        "انجام نشده"
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
    
    await message.answer(SUCCESS)
    
    await state.clear()