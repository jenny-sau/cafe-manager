import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load the .env file
load_dotenv()

# Retrieves the DB URL from the environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Creating the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# DB Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base for models
Base = declarative_base()

# Dependency  FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
