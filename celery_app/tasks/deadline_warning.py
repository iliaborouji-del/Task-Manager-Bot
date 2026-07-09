from celery import shared_task
from aiogram import Bot
from config import Config 
from datetime import datetime, timedelta
from sqlalchemy import select
from bot.database.connection import get_session_sync
from bot.database.models import Tasks

bot = Bot(token=Config.BOT_TOKEN)

@shared_task
def check_deadline():
    session = get_session_sync()
    now = datetime.now()
    
    result = session.execute(select(Tasks))
    tasks = result.scalars().all()
    
    for task in tasks:
        try:
            deadline_dt = datetime.strptime(task.deadline, "%Y-%m-%d  %H:%M")
        except Exception:
            continue
        
        if timedelta(0) < (deadline_dt - now) <= timedelta(hours=1) and not task.reminder_sent:
            text = (
                "کمتر از 1 ساعت تا پایان ددلاین باقی مانده!"
                f"📌 عنوان: {task.title}\n"
                f"⌛ ددلاین: {task.deadline}"
            )
            bot.send_message(task.user_id, text=text)
            task.reminder_sent = True
            
    session.commit()
    session.close()