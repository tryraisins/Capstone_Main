import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_database_session
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.auth import get_current_user
from app.crud import user_service
from app.auth import get_password_hash

# Create a mock SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:?check_same_thread=False"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def test_db():
    # Set up the database and yield session for tests
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    # Override the get_database_session dependency with test_db
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_database_session] = override_get_db
    client = TestClient(app)
    return client

@pytest.fixture(scope="module")
def mock_user():
    # Include the full_name field as required by the schema
    return UserCreate(username="testuser", email="test@example.com", full_name="Test User", password="password")

@pytest.fixture(scope="module")
def create_test_user(test_db, mock_user):
    hashed_password = get_password_hash(mock_user.password)
    user_service.create_user(test_db, mock_user, hashed_password=hashed_password)

# Test: Get list of users
def test_get_users(client, test_db, create_test_user):
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) > 0

# Test: Get user by ID
def test_get_user_by_id(client, test_db, create_test_user):
    test_user = user_service.get_user_by_username(test_db, "testuser")
    response = client.get(f"/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

# Test: Get user by username
def test_get_user_by_username(client):
    response = client.get("/users/name/testuser")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

# Test: Update user by ID
def test_update_user(client, test_db, mock_user):
    test_user = user_service.get_user_by_username(test_db, "testuser")
    update_data = {"username": "updateduser"}
    response = client.put(f"/users/{test_user.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"

# Test: Delete user by ID
def test_delete_user(client, test_db):
    test_user = user_service.get_user_by_username(test_db, "testuser")
    response = client.delete(f"/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Success"
