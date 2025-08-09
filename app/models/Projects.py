from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)

    owner_id = Column(Integer, ForeignKey("user.id"),nullable=False)
    owner=relationship("User",back_populates="projects")
    tasks=relationship("Task",back_populates="project",cascade="all, delete")


