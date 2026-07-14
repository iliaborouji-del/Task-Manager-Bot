from aiogram import filters, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.start import BotStates
from bot.keyboards.start import create_main_menu_keyboard
from bot.services.qrcode import verify
from bot.database.connection import session_scope
from bot.database.models import Tasks
from sqlalchemy import select
import jdatetime
from datetime import datetime, timezone, timedelta
from bot.templates.start import start_text
import urllib.parse

router = Router()

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def to_iran(dt: datetime) -> datetime:
    return ensure_utc(dt).astimezone(IRAN_TZ)

def format_jalali(dt: datetime) -> str:
    local = to_iran(dt)
    jdt = jdatetime.datetime.fromgregorian(datetime=local)
    return jdt.strftime("%Y/%m/%d  %H:%M")

@router.message(filters.CommandStart())
async def start(message: Message, state: FSMContext):
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("task_"):
        raw = parts[1]
        token = raw[len("task_"):]
        token = urllib.parse.unquote_plus(token)
        task_id = verify(token=token)
        if not task_id:
            await message.answer(text="لینک نامعتبر یا منقضی شده است.")
            return
        
        async with session_scope() as session:
            result = await session.execute(select(Tasks).where(Tasks.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                await message.answer(text="وظیفه پیدا نشد.")
                return
            
            created_text = format_jalali(task.created_at)
            if task.deadline:
                try:
                    deadline_text = format_jalali(task.deadline)
                except Exception:
                    deadline_text = str(task.deadline)
            else:
                deadline_text = "_"
                
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
            return

    await message.answer(text=start_text, reply_markup=create_main_menu_keyboard())
    await state.set_state(BotStates.waiting_for_main_menu_button)
    
@router.message(filters.Command("show_task"))
async def show_task_by_command(message: Message):
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.answer(text="لطفا payload را بعد از دستور وارد کنید. مثال:\n/show_task <payload>")
        return
    token = parts[1].strip()
    task_id = verify(token=token)
    if not task_id:
        await message.answer(text="payload نامعتبر یا منقضی شده است.")
        return
    
    async with session_scope() as session:
        result = session.execute(select(Tasks).where(Tasks.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            await message.answer(text="وظیفه پیدا نشد.")
            return
        
        created_text = format_jalali(task.created_at)
        if task.deadline:
            try:
                    deadline_text = format_jalali(task.deadline)
            except Exception:
                    deadline_text = str(task.deadline)
        else:
            deadline_text = "_"
                
        text = (
            f" شناسه: {task.id}\n"
            f"📌 عنوان: {task.title}\n"
            f"📝 توضیحات: {task.description}\n"
            f"📊 اولویت: {task.priority}\n"
            f"⌛ ددلاین (زمان پایان): {deadline_text}\n"
            f"📂 وضعیت: {task.status}\n"
            f"📆 اضافه شده در: {created_text}"
        )
        await message.answer(text=text)