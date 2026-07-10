import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "BROKER_URL")

app = Celery(
    "task_manager",
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

app.conf.beat_schedule = {
    "check-deadlines-every-1-minute": {
        "task": "celery_app.tasks.deadline_warning",
        "schedule": 60.0,
        "args": (),
    }
},