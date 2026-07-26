from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from bot.database.connection import session_scope
from bot.database.show_all_tasks import get_all_tasks
from io import BytesIO
from bot.keyboards.show_all_tasks import create_qr_keyboard
from bot.services.qrcode import get_or_create_qr
from bot.utils.datetime import jalali_string
from bot.keyboards.categories import create_show_all_tasks_categories_keyboard
from bot.database.categories import get_all_categories
from config import Config
import aiohttp

router = Router()

@router.message(F.text == "🗂️ نمایش همه وظایف")
async def select_category(message: Message):
    async with session_scope() as session:
            categories = await get_all_categories(
                session=session,
                user_id=message.from_user.id,
            )
    
            if not categories:
                await message.answer(text="هنوز هیچ دسته‌بندی ایجاد نکرده‌اید.")
                return
            
            await message.answer(
                text="دسته‌ بندی مورد نظر را برای نمایش انتخاب کنید.",
                reply_markup=create_show_all_tasks_categories_keyboard(categories)
        )

@router.callback_query(F.data.startswith("show_all_tasks_category:"))
async def show_all_tasks(call: CallbackQuery):
    category_id = int(call.data.split(":")[1])

    async with session_scope() as session:
        tasks = await get_all_tasks(
            session=session,
            user_id=call.from_user.id,
            category_id=category_id,
        )

        if not tasks:
            await call.message.answer(
                text="هیچ وظیفه‌ای در این دسته‌بندی ثبت نشده است."
            )
            await call.answer()
            return

        for task in tasks:
            created_text = jalali_string(task.created_at)

            if task.deadline:
                deadline_text = jalali_string(task.deadline)
            else:
                deadline_text = "_"

            category_name = (
                task.category.name
                if task.category
                else "-"
            )

            text = (
                "\u200F━━━━━━━━━━━━━━━━━━━━\n"
                f"\u200F🆔 شناسه: \u200E{task.id}\n"
                f"📁 دسته‌بندی: {category_name}\n"
                f"📌 عنوان: {task.title}\n"
                f"📝 توضیحات: {task.description}\n"
                f"📊 اولویت: {task.priority}\n"
                f"⌛ ددلاین: \u200E{deadline_text}\n"
                f"📂 وضعیت: {task.status}\n"
                f"📆 اضافه شده: \u200E{created_text}\n"
                "\u200F━━━━━━━━━━━━━━━━━━━━"
            )

            await call.message.answer(
                text=text,
                reply_markup=create_qr_keyboard(task.id),
            )

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
    
from bot.keyboards.start import create_main_menu_keyboard

@router.callback_query(F.data == "show_all_tasks_back")
async def show_all_tasks_back(call: CallbackQuery):
    await call.message.delete()

    await call.message.answer(
        text="منوی اصلی",
        reply_markup=create_main_menu_keyboard(),
    )

    await call.answer()