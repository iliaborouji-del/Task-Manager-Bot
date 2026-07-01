from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from datetime import datetime

from bot.states.start import BotStates

from bot.templates.add_task import (
    TITLE,
    DESCRIPTION,
    PRORITY,
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
    await state.set_state(BotStates.title)
    
@router.message(BotStates.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(DESCRIPTION)
    await state.set_state(BotStates.description)
    
@router.message(BotStates.description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(PRORITY)
    await state.set_state(BotStates.prority)
    
@router.message(BotStates.prority)
async def get_prority(message: Message, state: FSMContext):
    if message.text not in [
        "زیاد",
        "متوسط",
        "کم"
    ]:
        await message.answer(text="لطفا یکی از گزینه ها را وارد کنید.")
        return
    
    await state.update_data(prority=message.text)
    await message.answer(DEADLINE)
    await state.set_state(BotStates.deadline)
    
@router.message(BotStates.deadline)
async def get_deadline(message: Message, state: FSMContext):
    try:
        deadline = datetime.strptime(
            message.text,
            "%Y-%m-%d %H-%M"
        )
    except ValueError:
        await message.answer(
            "مثال شکل صحیح ورودی:\n\n"
            "1405-05-05 18:00"
        )
        return
    
    await state.update_data(deadline=message.text)
    await message.answer(STATUS)
    await state.set_state(BotStates.status)
    
@router.message(BotStates.status)
async def get_status(message: Message, state: FSMContext):
    if message.text not in [
        "انجام شده",
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