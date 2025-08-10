from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db import get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.Projects import Project
from app.models.user import User
from app.schemas.taskSchema import TaskCreate, TaskUpdate, TaskOut
from app.routes.authenticate import get_current_user
from app.core.celery_app import celery, send_email

router = APIRouter(
    tags=["Tasks"]
)

@router.post("/", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate project ownership
    project = db.query(Project).filter(
        Project.id == task.project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not yours")

    # 🐛 FIX: Validate assigned user exists if provided
    if task.assigned_user_id:
        assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
        if not assigned_user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    new_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status=task.status,
        priority=task.priority,
        project_id=task.project_id,
        assigned_user_id=task.assigned_user_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # 🐛 FIX: Send email notification when task is created and assigned
    if new_task.assigned_user_id:
        assigned_user = db.query(User).filter(User.id == new_task.assigned_user_id).first()
        if assigned_user:
            subject = f"New Task Assigned: {new_task.title}"
            content = f"You have been assigned a new task '{new_task.title}' (ID: {new_task.id})."
            send_email.delay(assigned_user.email, subject, content)
    
    return new_task

@router.get("/", response_model=List[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    due_date: Optional[str] = Query(None),  # 🐛 FIX: Should validate date format
    project_id: Optional[int] = Query(None),
    sort_by: Optional[str] = Query(None, regex="^(priority|due_date)$"),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).join(Project).filter(Project.owner_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if due_date:
        # 🐛 FIX: Add proper date validation and parsing
        try:
            parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            query = query.filter(Task.due_date.date() == parsed_date.date())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if sort_by:
        sort_attr = getattr(Task, sort_by)
        query = query.order_by(sort_attr)

    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Store old values for comparison
    old_status = task.status
    old_assigned_user_id = task.assigned_user_id
    
    # 🐛 FIX: Validate assigned user exists if being updated
    update_data = task_data.dict(exclude_unset=True)
    if "assigned_user_id" in update_data and update_data["assigned_user_id"]:
        assigned_user = db.query(User).filter(User.id == update_data["assigned_user_id"]).first()
        if not assigned_user:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    # Update task fields
    for field, value in update_data.items():
        setattr(task, field, value)

    # 🐛 FIX: Avoid calling task_data.dict() multiple times
    # Send status update notification
    if "status" in update_data and task.status != old_status:
        if task.assigned_user_id:
            assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
            if assigned_user:
                subject = f"Task Status Updated: {task.title}"
                content = f"The status of your task '{task.title}' (ID: {task.id}) has been updated to: {task.status}."
                send_email.delay(assigned_user.email, subject, content)

    # Send assignment notification
    if "assigned_user_id" in update_data and task.assigned_user_id != old_assigned_user_id:
        if task.assigned_user_id:  # 🐛 FIX: Check if new assignment is not None
            assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
            if assigned_user:
                subject = f"New Task Assigned: {task.title}"
                content = f"You have been assigned a new task '{task.title}' (ID: {task.id})."
                send_email.delay(assigned_user.email, subject, content)

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).join(Project).filter(
        Task.id == task_id,
        Project.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None