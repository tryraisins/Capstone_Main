import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_database_session
from sqlalchemy.pool import StaticPool

# Fetch the DATABASE_URL from the environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment")

# Detect if we are using SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # For PostgreSQL or other databases, use a simpler connection
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a testing session local
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure that all the tables are created in the test database
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database session dependency in FastAPI
app.dependency_overrides[get_database_session] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def setup_database():
    # Ensure the database is set up for each module test run
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown the database after the tests are completed
    Base.metadata.drop_all(bind=engine)
