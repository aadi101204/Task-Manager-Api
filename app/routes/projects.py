from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.Projects import Project
from app.schemas.projectSchema import ProjectOut
from app.schemas.projectSchema import ProjectCreate, ProjectUpdate, ProjectOut
from app.routes.authenticate import get_current_user
from app.models.user import User

router = APIRouter(
    tags=["Projects"]
)

@router.post("/",response_model=ProjectOut)
def create_project(
    project: ProjectCreate,
    db: Session=Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    new_project = Project(
        title=project.title,
        description=project.description,
        owner_id=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/",response_model=List[ProjectOut])
def get_projects(
    db:Session = Depends(get_db),
    current_user : User=Depends(get_current_user),
):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

@router.get("/{project_id}",response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project Not there")
    
    return project

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in project_data.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return None