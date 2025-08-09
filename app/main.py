from fastapi import FastAPI
from app.db import engine, Base
from app.models import user, Projects, task  

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

from app.api import authenticate, projects, task as task_routes

app.include_router(authenticate.router, prefix="/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])

@app.get("/")
def read_root():
    return {"message": "Task Manager API is running"}
