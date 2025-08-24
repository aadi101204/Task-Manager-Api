from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


from app.routes import authenticate, projects, task as task_routes


if os.getenv("ENVIRONMENT") == "development":
    from app.database_init import create_tables
    create_tables()

app = FastAPI(
    title="Task Manager API",
    description="A RESTful API for managing tasks and projects",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(authenticate.router, prefix="/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "message": "Task Manager API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy"}