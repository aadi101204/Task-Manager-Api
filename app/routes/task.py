from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.Projects import Project
from app.models.user import User
from app.schemas.taskSchema import TaskCreate, TaskUpdate, TaskOut
from app.routes.authenticate import get_current_user
from app.core.celery_app import send_email

router = APIRouter(
    tags=["Tasks"]
)

@router.post("/", response_model=TaskOut)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == task.project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found or not yours")

    new_task = Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        status=task.status,
        priority=task.priority,
        project_id=task.project_id,
        assigned_user_id=task.assigned_user_id  # ✅ updated
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    due_date: Optional[str] = Query(None),
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
        query = query.filter(Task.due_date == due_date)
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

    
    old_status = task.status
    old_assigned_user_id = task.assigned_user_id

    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)


    if "status" in task_data.dict(exclude_unset=True) and task.status != old_status:
        if task.assigned_user_id:
            assigned_user = db.query(User).filter(User.id == task.assigned_user_id).first()
            if assigned_user:
                subject = f"Task Status Updated: {task.title}"
                content = f"The status of your task '{task.title}' (ID: {task.id}) has been updated to: {task.status}."
                send_email.delay(assigned_user.email, subject, content)

    
    if "assigned_user_id" in task_data.dict(exclude_unset=True) and task.assigned_user_id != old_assigned_user_id:
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
