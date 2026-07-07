from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["bot.celery_app.tasks.deadline_warning"]
)

celery_app.conf.timezone = "Asia/Tehran"
celery_app.conf.enable_utc = False