from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


from contextlib import asynccontextmanager

from app.routes import authenticate, projects, task as task_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "development":
        from app.database_init import create_tables
        create_tables()
    yield

app = FastAPI(
    title="Task Manager API",
    description="A RESTful API for managing tasks and projects",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
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