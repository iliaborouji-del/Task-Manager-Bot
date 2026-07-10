from celery_app.celery_config import app
from datetime import datetime, timedelta, timezone
import logging
import requests
from dotenv import load_dotenv
import os
from bot.database.connection import get_session_sync
from bot.database.models import Tasks

load_dotenv()
BALE_TOKEN = os.getenv("BOT_TOKEN")
if not BALE_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment")

BALE_API_URL = f"https://tapi.bale.ai/bot{BALE_TOKEN}"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_deadlines(self):
    try:
        session = get_session_sync()
        now = datetime.now()
        threshold = timedelta(hours=1)
        
        tasks = session.query(Tasks).filter(Tasks.reminder_sent == False).all()
        
        for task in tasks:
            try:
                if not task.deadline:
                    continue
                
                if isinstance(task.deadline, str):
                    try:
                        deadline_dt = datetime.strptime(task.deadline, "%Y-%m-%d  %H:%M")
                    except:
                        logger.warning("Could not parse deadline for task.id=%s", task.id)
                        continue
                else:
                    deadline_dt = task.deadline if task.deadline.tzinfo else task.deadline.replace(tzinfo=timezone.utc)
                    
                delta = deadline_dt - now
                
                if timedelta(0) < delta <= threshold:
                    text = (
                        f"⚠️ یاد آوری ددلاین (کمتر از یک ساعت باقی مانده!!!):\n\n"
                        f"🆔 شناسه: {task.id}\n"
                        f"📌 عنوان: {task.title}\n"
                        f"⏳ ددلاین: {deadline_dt.strftime('%Y/%m/%d  %H:%M')}\n\n"
                        "لطفا وضعیت را بررسی کنید."
                    )
                    
                    payload = {
                        "chat_id": task.user_id,
                        "text": text,
                        "parse_mode": "HTML"
                    }
                    
                    try:
                        resp  = requests.post(BALE_API_URL, json=payload)
                        if resp.status_code == 200:
                            task.reminder_sent = True
                            session.add(task)
                            session.commit()
                            logger.info("Reminder sent for task id=%s", task.id)
                        else:
                            logger.error("Failed to send reminder for task id=%s, status=%s, body=%s", task.id, resp.status_code, resp.text)
                    except Exception as e:
                        logger.exception("Exception while sending reminder for task id=%s: %s", task.id, e)
                        raise self.retry(exc=e)
            except Exception as inner_e:
                logger.exception("Error processing task id=%s: %s", getattr(task, "id", None), inner_e)
                continue
            
        session.close()
    except Exception as e:
        logger.exception("check_deadline failed: %s", e)
        raise self.retry(exc=e)