from celery import Celery
from celery.schedules import crontab
from app.core.config import settings


celery = Celery(
    'task_manager',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
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
        'task': 'app.task.send_overdue_summary',
        'schedule': crontab(hour=6, minute=0),  
    },
}