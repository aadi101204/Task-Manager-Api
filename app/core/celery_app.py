from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from celery.schedules import crontab
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.db import localSession
from app.models.user import User
from app.models.task import Task, TaskStatus

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL is not set in environment variables.")

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'no-reply@yourdomain.com')

celery = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery.task
def send_email(to_email, subject, content):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[EMAIL] Sent to {to_email}, status code: {response.status_code}")
    except Exception as e:
        print(f"[EMAIL ERROR] Could not send to {to_email}: {e}")

def get_all_users():
    db: Session = localSession()
    try:
        return db.query(User).all()
    finally:
        db.close()

def get_overdue_tasks_for_user(user_id: int):
    db: Session = localSession()
    try:
        return db.query(Task).filter(
            Task.assigned_user_id == user_id,
            Task.status != TaskStatus.completed,
            Task.due_date < datetime.utcnow()
        ).all()
    finally:
        db.close()

@celery.task(name="tasks.send_overdue_summary")
def send_overdue_summary():
    print("[CRON] Running overdue summary job...")
    users = get_all_users()
    
    for user in users:
        try:
            overdue_tasks = get_overdue_tasks_for_user(user.id)
            
            if overdue_tasks:
                task_list = "\n".join(
                    [f"- {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})"
                     for task in overdue_tasks]
                )
                subject = "Daily Overdue Task Summary"
                content = (
                    f"Hello {user.username},\n\n"
                    f"You have the following overdue tasks:\n\n{task_list}\n\n"
                    "Please take action as soon as possible."
                )
                send_email.delay(user.email, subject, content)
                print(f"[CRON] Sent overdue summary to {user.email}")
            else:
                print(f"[CRON] No overdue tasks for {user.username}")
        
        except Exception as e:
            print(f"[CRON ERROR] Failed processing user {user.username}: {e}")

celery.conf.beat_schedule = {
    'send-daily-overdue-summary': {
        'task': 'tasks.send_overdue_summary',
        'schedule': crontab(hour=6, minute=0),
    },
}
