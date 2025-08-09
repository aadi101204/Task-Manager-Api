from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.taskSchema import TaskOut

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title:Optional[str]= None
    description: Optional[str] = None

class ProjectOut(ProjectBase):
    id: int
    owner_id: int
    tasks: List[TaskOut] = []

    class Config:
        from_attributes = True

