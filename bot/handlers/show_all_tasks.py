from aiogram import F, Router
from aiogram.types import Message
from bot.database.connection import get_session
from bot.database.show_all_tasks import get_all_tasks
from datetime import datetime
import jdatetime

router = Router()

@router.message(F.text == "🗂️ نمایش همه وظایف")
async def show_all_tasks(message: Message):
    session = await get_session()
    tasks = await get_all_tasks(session=session, user_id=message.from_user.id)

    if not tasks:
        await message.answer(text="هیچ وظیفه ای ثبت نشده است.")
        return
    
    for task in tasks:
        jalali_created = jdatetime.datetime.fromgregorian(datetime=task.created_at)
        created_text = jalali_created.strftime("%Y/%m/%d  %H:%M")
        
        try:
            deadline_dt = datetime.strptime(task.deadline, "%Y/%m/%d  %H:%M")
            jalali_deadline = jdatetime.datetime.fromgregorian(datetime=deadline_dt)
            deadline_text = jalali_deadline.strftime("%Y/%m/%d  %H:%M")
        except:
            deadline_text = task.deadline
            
        text = (
            f"🆔 شناسه: {task.id}\n"
            f"📌 عنوان: {task.title}\n"
            f"📝 توضیحات: {task.description}\n"
            f"📊 اولویت: {task.priority}\n"
            f"⌛ ددلاین(زمان پایان): {deadline_text}\n"
            f"📂 وضعیت: {task.status}\n"
            f"📆 اضافه شده در: {created_text}"
        )
        
        await message.answer(text=text)