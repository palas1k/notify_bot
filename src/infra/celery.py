import asyncio

from celery import Celery
from celery.schedules import crontab

from src.config import get_config

cfg = get_config()

celery_event_loop = asyncio.get_event_loop()
app = Celery('notbot', broker=cfg.celery.url)
app.autodiscover_tasks(["src.usecases.tasks"])
app.conf.beat_schedule = {
    "every-day": {
        "task": "src.usecases.tasks.every_day",
        "schedule": crontab(minute="*/1", hour="0-23"),
    },
}
app.conf.update(timezone="Europe/Moscow")
