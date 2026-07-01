from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from datetime import datetime
import jdatetime

from bot.states.add_task import AddTaskStates

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
    await message.answer(PRIORITY)
    await state.set_state(AddTaskStates.priority)
    
@router.message(AddTaskStates.priority)
async def get_priority(message: Message, state: FSMContext):
    if message.text not in [
        "زیاد",
        "متوسط",
        "کم"
    ]:
        await message.answer(text="لطفا یکی از گزینه ها را وارد کنید.")
        return
    
    await state.update_data(priority=message.text)
    await message.answer(DEADLINE)
    await state.set_state(AddTaskStates.deadline)
    
@router.message(AddTaskStates.deadline)
async def get_deadline(message: Message, state: FSMContext):
    try:
        deadline_jalali = jdatetime.datetime.strptime(
            message.text,
            "%Y-%m-%d %H:%M"
        )
        
        deadline = deadline_jalali.togregorian()
        
    except ValueError:
        await message.answer(
            "مثال شکل صحیح ورودی:\n\n"
            "1405-05-05 18:00"
        )
        return
    
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