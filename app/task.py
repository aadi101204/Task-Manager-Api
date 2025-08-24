from celery import current_app as celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.db import SessionLocal
from app.models.user import User
from app.models.task import Task, TaskStatus


SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'no-reply@yourdomain.com')

@celery.task(bind=True, retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_email(self, to_email, subject, content):
    if not SENDGRID_API_KEY:
        print("[EMAIL] Warning: SENDGRID_API_KEY not configured")
        return False
        
    try:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=content,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[EMAIL] Sent to {to_email}, status: {response.status_code}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to_email}: {e}")
        # Retry the task
        raise self.retry(exc=e)

@celery.task
def send_overdue_summary():
    print("[CRON] Running overdue summary job...")
    
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        
        for user in users:
            try:
                overdue_tasks = db.query(Task).filter(
                    Task.assigned_user_id == user.id,
                    Task.status != TaskStatus.completed,
                    Task.due_date < datetime.timezone.utc()
                ).all()
                
                if overdue_tasks:
                    task_list = "\n".join([
                        f"- {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})"
                        for task in overdue_tasks
                    ])
                    
                    subject = "Daily Overdue Task Summary"
                    content = (
                        f"Hello {user.username},\n\n"
                        f"You have {len(overdue_tasks)} overdue task(s):\n\n"
                        f"{task_list}\n\n"
                        "Please take action as soon as possible.\n\n"
                        "Best regards,\nTask Manager Team"
                    )
                    
                    send_email.delay(user.email, subject, content)
                    print(f"[CRON] Queued overdue summary for {user.email}")
                else:
                    print(f"[CRON] No overdue tasks for {user.username}")
                    
            except Exception as e:
                print(f"[CRON ERROR] Failed processing user {user.username}: {e}")
    finally:
        db.close()