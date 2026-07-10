import jdatetime
from datetime import datetime, timezone, timedelta
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from bot.database.delete_task import delete_task_by_id
from bot.database.connection import session_scope
from bot.keyboards.show_tasks import create_change_status_keyboard
from bot.database.show_tasks import show_not_completed_tasks
from sqlalchemy import select
from bot.database.models import Tasks

router = Router()
# ---------- function for time ----------
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))
#----------
def datetime_utc(dt: datetime) -> datetime:
    if dt is None:
        raise ValueError("datetime is None")
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def iran_time(dt: datetime) -> datetime:
    dt_utc = datetime_utc(dt)
    return dt_utc.astimezone(IRAN_TZ)

def format_jalali_dt(dt: datetime, fmt: str = "%Y/%m/%d  %H:%M") -> str:
    local = iran_time(dt)
    jalali = jdatetime.datetime.fromgregorian(datetime=local)
    return jalali.strftime(fmt)

def deadline_string(deadline_str: str, fmt: str = "%Y-%m-%d  %H:%M"):
    try:
        dt = datetime.strptime(deadline_str, fmt)
        return dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None

# ---------- continue -----------
@router.message(F.text == "📋 نمایش وظایف انجام نشده")
async def show_tasks(message: Message):
    async with session_scope() as session:
        tasks = await show_not_completed_tasks(session=session, user_id=message.from_user.id)
        
        if not tasks:
            await message.answer(text="هیچ وظیفه انجام نشده ای وجود ندارد.")
            return
        
        for task in tasks:
            try:
                created_text = format_jalali_dt(task.created_at)
            except Exception:
                created_text = str(task.created_at)
                
            parsed_deadline = None
            if  isinstance(task.deadline, str):
                parsed_deadline = deadline_string(task.deadline)
            elif isinstance(task.deadline, datetime):
                parsed_deadline = task.deadline if task.deadline.tzinfo else task.deadline.replace(tzinfo=timezone.utc)
                
            if parsed_deadline:
                try:
                    deadline_text = format_jalali_dt(parsed_deadline)
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
            
            await message.answer(
                text=text,
                reply_markup=create_change_status_keyboard(task.id)
            )
        
@router.callback_query(F.data.startswith("task:"))
async def change_status(call: CallbackQuery):
    async with session_scope() as session:
        _, task_id, new_status = call.data.split(":")
        task_id = int(task_id)
        result = await session.execute(select(Tasks).where(Tasks.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            await call.answer(text="وظیفه پیدا نشد!", show_alert=True)
            return
        
        task.status = new_status
        if new_status == "انجام شده ✅":
            task.completed_at = datetime.now(timezone.utc)
            
        await session.commit()
        
        try:
            created_text = format_jalali_dt(task.created_at)
        except Exception:
            created_text = str(task.created_at)
                
        parsed_deadline = None
        if  isinstance(task.deadline, str):
            parsed_deadline = deadline_string(task.deadline)
        elif isinstance(task.deadline, datetime):
            parsed_deadline = task.deadline if task.deadline.tzinfo else task.deadline.replace(tzinfo=timezone.utc)
            
        if parsed_deadline:
            try:
                deadline_text = format_jalali_dt(parsed_deadline)
            except Exception:
                deadline_text = str(task.deadline)
                
                
        new_text = (
            f"🆔 شناسه: {task.id}\n"
            f"📌 عنوان: {task.title}\n"
            f"📝 توضیحات: {task.description}\n"
            f"📊 اولویت: {task.priority}\n"
            f"⌛ ددلاین (زمان پایان): {deadline_text}\n"
            f"📂 وضعیت: {task.status}\n"
            f"📆 اضافه شده در: {created_text}"
        )
            
        if new_status == "انجام شده ✅":
            await call.message.edit_text(text=new_text, reply_markup=None)
        else:
            await call.message.answer(text=new_text, reply_markup=create_change_status_keyboard(task.id))
            
        await call.answer(text="وضعیت با موفقیت تغییر کرد.")
        
@router.callback_query(F.data.startswith("delete:"))
async def delete_task(call: CallbackQuery):
    async with session_scope() as session:
        task_id = int(call.data.split(":")[1])
        await delete_task_by_id(session=session, task_id=task_id)
        try:
            await call.message.edit_text(text="وظیفه حذف شد.", reply_markup=None)
        except Exception:
            pass

        await call.answer()