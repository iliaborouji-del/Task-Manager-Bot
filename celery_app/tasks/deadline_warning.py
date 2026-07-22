from celery_app.celery_config import app
from datetime import timedelta
import logging
import requests

from bot.database.connection import get_session_sync
from bot.database.models import Tasks
from bot.utils.datetime import (
    now_iran,
    iran_to_naive,
    jalali_string,
)
from config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def check_deadlines(self):
    session = None

    try:
        session = get_session_sync()

        now = iran_to_naive(now_iran())
        threshold = timedelta(hours=1)

        tasks = (
            session.query(Tasks)
            .filter(Tasks.reminder_sent == False)
            .all()
        )

        logger.info("Checking %s pending tasks.", len(tasks))

        if Config.SOURCE == "telegram":
            send_url = (
                f"https://api.telegram.org/"
                f"bot{Config.BOT_TOKEN}/sendMessage"
            )
        else:
            send_url = (
                f"{Config.API_BASE_BALE}/"
                f"bot{Config.BOT_TOKEN}/sendMessage"
            )

        for task in tasks:

            try:
                if task.status == "انجام شده ✅":
                    continue
                if task.deadline is None:
                    continue

                deadline_dt = task.deadline
                delta = deadline_dt - now

                if timedelta(0) < delta <= threshold:

                    text = (
                        "⚠️ یادآوری ددلاین\n\n"
                        f"🆔 شناسه: {task.id}\n"
                        f"📌 عنوان: {task.title}\n"
                        f"⏳ ددلاین: {jalali_string(deadline_dt)}\n\n"
                        "کمتر از یک ساعت تا پایان این وظیفه باقی مانده است!!!"
                    )

                    payload = {
                        "chat_id": task.user_id,
                        "text": text,
                        "parse_mode": "HTML",
                    }
                    
                    response = requests.post(
                        send_url,
                        json=payload,
                        timeout=15,
                    )
                    if response.status_code == 200:
                        task.reminder_sent = True
                        session.commit()
                        logger.info(
                            "Reminder sent successfully. task=%s user=%s",
                            task.id,
                            task.user_id,
                        )
                    else:
                        logger.error(
                            "Failed sending reminder. "
                            "task=%s status=%s body=%s",
                            task.id,
                            response.status_code,
                            response.text,
                        )
            except Exception as e:
                logger.exception("Error processing task id=%s : %s", getattr(task, "id", None), e,)
                continue
    except Exception as e:
        logger.exception("check_deadlines failed: %s", e)
        raise self.retry(exc=e)

    finally:
        if session is not None:
            session.close()
        logger.info("Deadline checking completed.")