from aiogram import F, Router
from aiogram.types import Message
from bot.database.connection import session_scope
from bot.database.show_all_tasks import get_all_tasks
from datetime import datetime, timedelta, timezone
import jdatetime

router = Router()

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

def datetime_as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def format_jalali_dt(dt: datetime, fmt: str = "%Y/%m/%d  %H:%M") -> str:
    dt_utc = datetime_as_utc(dt)
    local = dt_utc.astimezone(IRAN_TZ)
    jalali = jdatetime.datetime.fromgregorian(datetime=local)
    return jalali.strftime(fmt)

@router.message(F.text == "🗂️ نمایش همه وظایف")
async def show_all_tasks(message: Message):
    async with session_scope() as session:
        tasks = await get_all_tasks(session=session, user_id=message.from_user.id)

        if not tasks:
            await message.answer(text="هیچ وظیفه ای ثبت نشده است.")
            return
        
        for task in tasks:
            jalali_created = format_jalali_dt(task.created_at)
            created_text = jalali_created
            
            try:
                if isinstance(task.deadline, datetime):
                    deadline_text = format_jalali_dt(task.deadline)
                else:
                    deadline_dt = datetime.strptime(task.deadline, "%Y-%m-%d  %H:%M")
                    deadline_dt = deadline_dt.replace(tzinfo=timezone.utc)
                    deadline_text = format_jalali_dt(deadline_dt)
            except Exception:
                deadline_text = str(task.deadline)
                
            text = (
                f"🆔 شناسه: {task.id}\n"
                f"📌 عنوان: {task.title}\n"
                f"📝 توضیحات: {task.description}\n"
                f"📊 اولویت: {task.priority}\n"
                f"⌛ ددلاین (زمان پایان): {deadline_text}\n"
                f"📂 وضعیت: {task.status}\n"
                f"📆 اضافه شده در: {created_text}"
            )
            
            await message.answer(text=text)