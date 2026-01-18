# Task Manager API

A RESTful API for managing tasks and projects built with FastAPI, SQLAlchemy, and PostgreSQL. Features user authentication, project management, and task assignment with filtering and sorting capabilities.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Project Management**: Create, read, update, and delete projects
- **Task Management**: Full CRUD operations for tasks with status and priority tracking
- **Task Assignment**: Assign tasks to users
- **Filtering & Sorting**: Filter tasks by status, priority, due date, and project
- **User Authorization**: Users can only access their own projects and tasks

## Tech Stack

- **Frontend**: React, TypeScript, Vite
- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens with passlib for password hashing
- **Background Tasks**: Celery with Redis (setup ready)
- **Validation**: Pydantic schemas

## Database Schema

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│      User       │       │    Project      │       │      Task       │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────┤ id (PK)         │◄──────┤ id (PK)         │
│ username        │   │   │ title           │   │   │ title           │
│ email           │   │   │ description     │   │   │ description     │
│ hashed_password │   │   │ owner_id (FK)   │   │   │ due_date        │
└─────────────────┘   │   └─────────────────┘   │   │ status          │
                      │                         │   │ priority        │
                      └─────────────────────────┘   │ project_id (FK) │
                                                    │ assigned_user_id│
                                                    └─────────────────┘

Relationships:
- User → Projects (One-to-Many): A user can own multiple projects
- Project → Tasks (One-to-Many): A project can have multiple tasks
- User → Tasks (One-to-Many): A user can be assigned to multiple tasks
```

### Entity Descriptions

**User**

- Stores user credentials and profile information
- Each user can own multiple projects and be assigned to multiple tasks

**Project**

- Contains project metadata (title, description)
- Owned by a single user
- Can contain multiple tasks

**Task**

- Represents individual work items
- Belongs to a project
- Can be assigned to a user
- Has status (pending, in_progress, completed, overdue) and priority (low, medium, high)

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Celery background tasks)
- Node.js & npm (for Frontend)

### Frontend Setup

The frontend is located in the `frontend/` directory.

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```
   Access at `http://localhost:5173`

### Deployment & Remote Access
For instructions on how to access the app from other devices or deploy to the cloud, see [DEPLOYMENT.md](DEPLOYMENT.md).

### Local Backend Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Task-Manager-Api
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   Create a `.env` file in the root directory:

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/taskmanager
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Database Setup**

   ```bash
   # Create PostgreSQL database
   createdb taskmanager

   # Run the application (this will create tables automatically)
   uvicorn app.main:app --reload
   ```

6. **Start the development server**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Production Deployment

#### Using Docker (Recommended)

1. **Create Dockerfile**

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .
   EXPOSE 8000

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Create docker-compose.yml**

   ```yaml
   version: "3.8"

   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/taskmanager
         - SECRET_KEY=production-secret-key
       depends_on:
         - db
         - redis

     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=taskmanager
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data

     redis:
       image: redis:6-alpine

     worker:
       build: .
       command: celery -A app.core.celery_app worker --loglevel=info
       depends_on:
         - redis
         - db

   volumes:
     postgres_data:
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

#### Manual Deployment

1. **Install dependencies on server**
2. **Configure environment variables**
3. **Set up PostgreSQL and Redis**
4. **Use a WSGI server like Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## Authentication & Getting a Token

### 1. Register a new user

```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "email": "john@example.com",
       "password": "secretpassword"
     }'
```

### 2. Login to get access token

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=johndoe&password=secretpassword"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Use the token for authenticated requests

```bash
curl -X GET "http://localhost:8000/projects/" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `GET /auth/users` - List all users
- `DELETE /auth/{user_id}` - Delete user

### Projects

- `POST /projects/` - Create project
- `GET /projects/` - List user's projects
- `GET /projects/{id}` - Get specific project
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Tasks

- `POST /tasks/` - Create task
- `GET /tasks/` - List tasks (with filtering)
- `GET /tasks/{id}` - Get specific task
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Query Parameters for Task Filtering

- `status` - Filter by task status (pending, in_progress, completed, overdue)
- `priority` - Filter by priority (low, medium, high)
- `due_date` - Filter by due date
- `project_id` - Filter by project
- `sort_by` - Sort by priority or due_date
- `skip` & `limit` - Pagination

## Celery Worker Setup

The application is configured to use Celery for background task processing with Redis as the message broker.

### Configuration

The Celery configuration is located in `app/core/celery_app.py` (currently empty but ready for setup).

### Setting up Celery

1. **Configure Celery App** (add to `app/core/celery_app.py`):

   ```python
   from celery import Celery

   celery_app = Celery(
       "task_manager",
       broker="redis://localhost:6379/0",
       backend="redis://localhost:6379/0",
       include=["app.tasks"]
   )

   celery_app.conf.update(
       task_serializer="json",
       accept_content=["json"],
       result_serializer="json",
       timezone="UTC",
       enable_utc=True,
   )
   ```

2. **Create background tasks** (`app/tasks.py`):

   ```python
   from app.core.celery_app import celery_app

   @celery_app.task
   def send_notification_email(user_email: str, message: str):
       # Send email notification
       pass

   @celery_app.task
   def update_overdue_tasks():
       # Mark overdue tasks
       pass
   ```

3. **Start Celery worker**:

   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   ```

4. **Start Celery beat scheduler** (for periodic tasks):
   ```bash
   celery -A app.core.celery_app beat --loglevel=info
   ```

### Common Background Task Use Cases

- Send email notifications when tasks are assigned
- Update task statuses (mark overdue tasks)
- Generate reports
- Data cleanup and maintenance

## Project Structure

```
app/
├── core/
│   ├── celery_app.py      # Celery configuration
│   ├── config.py          # Environment configuration
│   └── security.py        # Authentication utilities
├── models/
│   ├── user.py           # User model
│   ├── Projects.py       # Project model
│   └── task.py           # Task model
├── routes/
│   ├── authenticate.py   # Auth endpoints
│   ├── projects.py       # Project endpoints
│   └── task.py          # Task endpoints
├── schemas/
│   ├── userSchema.py     # User Pydantic models
│   ├── projectSchema.py  # Project Pydantic models
│   └── taskSchema.py     # Task Pydantic models
├── db.py                 # Database configuration
└── main.py               # FastAPI application
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Database Migrations

The application currently uses SQLAlchemy's `create_all()` method. For production, consider using Alembic for database migrations:

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
