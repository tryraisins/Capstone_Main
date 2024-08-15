import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# Load environment variables from .env file
load_dotenv()

# Load the DATABASE_URL from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Create a session maker bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_database_session():
    # Provide a database session to be used in dependency injection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
