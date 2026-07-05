import jdatetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from bot.database.connection import get_session
from bot.database.connection import get_session
from bot.keyboards.show_tasks import create_change_status_keyboard
from bot.database.show_tesk import show_not_done_tasks
from sqlalchemy import select
from bot.database.models import Tasks

router = Router()

@router.message(F.text == "📋 نمایش وظیفه‌ها")
async def show_tasks(message: Message):
    session = await get_session()
    tasks = await show_not_done_tasks(session=session, user_id=message.from_user.id)
    
    if not tasks:
        await message.answer(text="هیچ وظیفه انجام نشده ای وجود ندارد.")
        return
    
    for task in tasks:
        jalali_created = jdatetime.datetime.fromgregorian(datetime=task.created_at)
        created_text = jalali_created.strftime("%Y-%m%d  %H:%M")
        
        jalali_deadline = jdatetime.datetime.fromgregorian(datetime=task.deadline)
        deadline_text = jalali_deadline.strftime("%Y-%m%d  %H:%M")
        
        text = (
            f"شناسه: {task.id}\n"
            f"عنوان: {task.title}\n"
            f"توضیحات: {task.description}\n"
            f"اولویت: {task.priority}\n"
            f"ددلاین(زمان پایان): {deadline_text}\n"
            f"وضعیت: {task.status}\n"
            f"اضافه شده در: {created_text}"
        )
        
        await message.answer(
            text=text,
            reply_markup=create_change_status_keyboard(task.id)
        )
        
@router.callback_query(F.data.startswith)
async def change_status(call: CallbackQuery):
    _, task_id, new_status = call.data.split(":")
    task_id = int(task_id)
    
    session = await get_session()
    
    result = await session.execute(select(Tasks).where(Tasks.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        await call.answer(text="وظیفه پیدا نشد!", show_alert=True)
        return
    
    task.status = new_status
    await session.commit()
    
    await call.message.answer(
        text=f"وضعیت به:{new_status}، تغییر کرد."
    )