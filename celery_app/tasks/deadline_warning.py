from celery_app.celery_config import celery_app
from aiogram import Bot
from config import Config

bot = Bot(token=Config.BOT_TOKEN)

@celery_app.task
def send_deadline_warning(user_id: int, title: str, deadline: str):
    text = (
        "فقط یک روز تا پایان ددلاین باقی مانده!\n\n"
        f"📌عنوان: {title}\n"
        f"⏳ددلاین: {deadline}"
    )
    bot.send_message(user_id, text)