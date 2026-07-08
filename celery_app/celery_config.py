from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["bot.celery_app.tasks.deadline_warning"]
)

celery_app.conf.timezone = "Asia/Tehran"
celery_app.conf.enable_utc = False

celery_app.conf.beat_schedule = {
    "check-deadline-every-5-minutes": {
        "task": "celery_app.tasks/deadline_warning.check_deadline",
        "schedule": 300.0,
    }
}