from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as sqlEnum
from sqlalchemy.orm import relationship
from app.db import Base

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(sqlEnum(TaskStatus), default=TaskStatus.pending)
    priority = Column(sqlEnum(TaskPriority), default=TaskPriority.medium)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)  
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
