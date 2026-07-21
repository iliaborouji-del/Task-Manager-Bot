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

def format_jalali(dt: datetime, fmt: str = "%Y/%m/%d  %H:%M") -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(IRAN_TZ)

    jalali = jdatetime.datetime.fromgregorian(datetime=dt)
    return jalali.strftime(fmt)

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