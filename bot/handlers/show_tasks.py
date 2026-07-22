import jdatetime
from datetime import datetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from bot.database.delete_task import delete_task_by_id
from bot.database.connection import session_scope
from bot.keyboards.show_tasks import (
    create_change_status_keyboard,
    create_delete_keyboard
)
from bot.utils.datetime import (
    jalali_string,
    naive_to_iran,
)
from bot.services.qrcode import get_or_create_qr
from bot.database.show_tasks import show_not_completed_tasks
from sqlalchemy import select
from bot.database.models import Tasks
from io import BytesIO
from config import Config
import aiohttp
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "📋 نمایش وظایف انجام نشده")
async def show_tasks(message: Message):
    async with session_scope() as session:
        tasks = await show_not_completed_tasks(session=session, user_id=message.from_user.id)
        
        if not tasks:
            await message.answer(text="هیچ وظیفه انجام نشده ای وجود ندارد.")
            return
        
        for task in tasks:
            try:
                created_text = jalali_string(task.created_at)
            except Exception:
                created_text = str(task.created_at)
                
            if task.deadline:
                deadline_text = jalali_string(task.deadline)
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
            
            if task.status == "در حال انجام ⏳":
                await message.answer(
                    text=text,
                    reply_markup=create_change_status_keyboard(task.id, "در حال انجام ⏳")
                )
            else:
                await message.answer(
                    text=text,
                    reply_markup=create_change_status_keyboard(task.id, "انجام نشده ⭕")
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
            task.completed_at = naive_to_iran(datetime.now()).replace(tzinfo=None)
            
        await session.commit()
        logger.info(
            "Task %s status changed to %s",
            task.id,
            new_status
        )
        
        try:
            created_text = jalali_string(task.created_at)
        except Exception:
            created_text = str(task.created_at)
        
        if task.deadline:
            deadline_text = jalali_string(task.deadline)
        else:
            deadline_text = "_"
                
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
            await call.message.edit_text(
                text=new_text, 
                reply_markup=create_delete_keyboard(task_id)
            )
        elif new_status == "در حال انجام ⏳":
            await call.message.edit_text(
                text=new_text, 
                reply_markup=create_change_status_keyboard(task.id, "در حال انجام ⏳")
            )
        else:
            await call.message.edit_text(
                text=new_text, 
                reply_markup=create_change_status_keyboard(task.id, "انجام نشده ⭕")
            )
            
        await call.answer(text="وضعیت با موفقیت تغییر کرد.")
        
@router.callback_query(F.data.startswith("delete:"))
async def delete_task(call: CallbackQuery):
    async with session_scope() as session:
        task_id = int(call.data.split(":")[1])
        await delete_task_by_id(session=session, task_id=task_id)
        logger.info(
            "Delete requested for task=%s",
            task_id
        )
        try:
            await call.message.edit_text(text="وظیفه حذف شد.", reply_markup=None)
        except Exception:
            pass

        await call.answer()

async def send_photo_to_bale(chat_id, img_bytes, caption=""):
    url = f"{Config.API_BASE_BALE}/bot{Config.BOT_TOKEN}/sendPhoto"
        
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