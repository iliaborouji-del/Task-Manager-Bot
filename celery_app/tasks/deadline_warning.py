from celery_app.celery_config import app
from datetime import datetime, timedelta, timezone
import logging
import requests
from bot.database.connection import get_session_sync
from bot.database.models import Tasks
from config import Config

BALE_TOKEN = Config.BOT_TOKEN
if not BALE_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment")

BALE_API_URL = Config.API_BASE_BALE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_deadlines(self):
    try:
        session = get_session_sync()
        now = datetime.now(timezone.utc)
        threshold = timedelta(hours=1)
        
        tasks = session.query(Tasks).filter(Tasks.reminder_sent == False).all()
        logger.info(
            "Checking %s pending tasks.",
            len(tasks)
        )
        
        for task in tasks:
            try:
                if not task.deadline:
                    continue
                
                deadline_dt = task.deadline if task.deadline.tzinfo else task.deadline.replace(tzinfo=timezone.utc)
                deadline_text = deadline_dt.astimezone(IRAN_TZ).strftime("%Y/%m/%d  %H:%M")
                    
                delta = deadline_dt - now
                
                if timedelta(0) < delta <= threshold:
                    text = (
                        f"⚠️ یاد آوری ددلاین (کمتر از یک ساعت باقی مانده!!!):\n\n"
                        f"🆔 شناسه: {task.id}\n"
                        f"📌 عنوان: {task.title}\n"
                        f"⏳ ددلاین: {deadline_text}\n\n"
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
    except Exception as e:
        logger.exception("check_deadline failed: %s", e)
        raise self.retry(exc=e)
    finally:
        session.close()
        logger.info("Deadline checking completed.")