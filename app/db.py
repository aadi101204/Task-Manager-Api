import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")

engine=create_engine(DATABASE_URL)
localSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base=sqlalchemy.orm.declarative_base()



def get_db():
    db= localSession()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)