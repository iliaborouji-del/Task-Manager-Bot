from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from bot.database.connection import session_scope
from bot.database.show_all_tasks import get_all_tasks
from io import BytesIO
from bot.keyboards.show_all_tasks import create_qr_keyboard
from bot.services.qrcode import get_or_create_qr
from datetime import datetime, timedelta, timezone
from config import Config
import jdatetime
import aiohttp

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
            
            await message.answer(text=text, reply_markup=create_qr_keyboard(task.id))

async def send_photo_to_bale(chat_id, img_bytes, caption=""):
    url = f"{Config.API_BASE}/bot{Config.BOT_TOKEN}/sendPhoto"
        
    bio = BytesIO(img_bytes)
    bio.name = "qr-code.png"
        
    data = aiohttp.FormData()
    data.add_field('chat_id', str(chat_id))
    data.add_field('caption', caption)
    data.add_field('photo', bio, filename='qr-code.png', content_type='image/png')
        
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            result = await response.json()
            return result

@router.callback_query(F.data.startswith("qr:"))
async def send_qr_code(call: CallbackQuery):
    _, task_id_str = call.data.split(":")
    try:
        task_id = int(task_id_str)
    except ValueError:
        await call.answer(text="شناسه تسک نامعتبر است.", show_alert=True)
        return
    
    img_bytes = await get_or_create_qr(task_id=task_id)
    if not img_bytes:
        await call.message.answer(text="بارکد ساخته نشد یا بارکد منقضی شده است.")
        await call.answer()
        return
    
    if Config.SOURCE == "telegram":
        await call.message.answer_photo(
            photo=BufferedInputFile(img_bytes, "qr-code.png"),
            caption=f"بارکد وظیفه {task_id}"
        )
    else:
        # await call.message.answer_photo(photo=BufferedInputFile(bio, bio.name), caption=f"بارکد وظیفه {task_id}")
        await send_photo_to_bale(call.from_user.id, img_bytes, f"بارکد وظیفه {task_id}")
        
    await call.answer()