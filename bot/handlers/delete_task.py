from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from bot.database.delete_task import delete_task_by_id
from bot.keyboards.delete_task import create_delete_keyboard
from bot.database.connection import get_session
from bot.database.show_all_tasks import get_all_tasks

router = Router()

@router.message(F.text == "🗑️ حذف وظیفه")
async def delete_task_start(message: Message):
    session = await get_session()
    tasks = await get_all_tasks(session, message.from_user.id)

    if not tasks:
        await message.answer(text="هیچ وظیفه ای برای حذف وجود ندارد.")
        return
    
    for task in tasks:
        text = f"🆔شناسه: {task.id}\n📌عنوان: {task.title}"
        await message.answer(text=text, reply_markup=create_delete_keyboard(task.id))
        
@router.callback_query(F.data.startswith("delete:"))
async def delete_task(call: CallbackQuery):
    task_id = int(call.data.split(":")[1])
    
    session = await get_session()
    await delete_task_by_id(session=session, task_id=task_id)
    await call.message.answer(text="وظیفه حذف شد.")
    await call.answer()