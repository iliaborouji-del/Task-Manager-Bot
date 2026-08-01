from aiogram import filters, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.start import BotStates
from bot.keyboards.start import create_main_menu_keyboard
from bot.services.qrcode import verify
from bot.database.connection import session_scope
from bot.database.models import Tasks
from sqlalchemy import select
from bot.utils.datetime import jalali_string
from bot.templates.start import start_text
from bot.database.users import register_user
import urllib.parse

router = Router()

@router.message(filters.CommandStart())
async def start(message: Message, state: FSMContext):
    async with session_scope() as session:
        await register_user(
            session=session,
            user_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
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
        
            result = await session.execute(select(Tasks).where(Tasks.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                await message.answer(text="وظیفه پیدا نشد.")
                return
            
            created_text = jalali_string(task.created_at)
            if task.deadline:
                try:
                    deadline_text = jalali_string(task.deadline)
                except Exception:
                    deadline_text = str(task.deadline)
            else:
                deadline_text = "_"
                
            text = (
                "\u200F━━━━━━━━━━━━━━━━━━\n"
                f"\u200F🆔 شناسه:  \u200E{task.id}\n"
                f"📌 عنوان:  {task.title}\n"
                f"📝 توضیحات:  {task.description}\n"
                f"📊 اولویت:  {task.priority}\n"
                f"⌛ ددلاین (زمان پایان): \u200E{deadline_text}\n"
                f"📂 وضعیت:  {task.status}\n"
                f"📆 اضافه شده:  \u200E{created_text}\n"
                "\u200F━━━━━━━━━━━━━━━━━━\n"
            )
            await message.answer(text=text)
            return

    await message.answer(text=start_text, reply_markup=create_main_menu_keyboard())
    await state.set_state(BotStates.waiting_for_main_menu_button)