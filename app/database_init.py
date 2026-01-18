from app.db import engine, Base

def create_tables():
    Base.metadata.create_all(bind=engine)

def init_db():
    create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()