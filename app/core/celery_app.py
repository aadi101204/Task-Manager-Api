from celery import Celery
from celery.schedules import crontab
import os


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


celery = Celery(
    'task_manager',
    broker=REDIS_URL,
    backend=REDIS_URL
)


celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)


from app.task import send_email, send_overdue_summary

celery.conf.beat_schedule = {
    'send-daily-overdue-summary': {
        'task': 'app.tasks.send_overdue_summary',
        'schedule': crontab(hour=6, minute=0),  
    },
}