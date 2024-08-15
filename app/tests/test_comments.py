import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_database_session, Base
from app.models import User
from app.auth import generate_access_token
import os
from app.tests.test_db import test_db


# Retrieve configuration values
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "30"))



# Set up in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_database_session] = override_get_db
    client = TestClient(app)
    return client

@pytest.fixture(scope="module")
def auth_token(test_db):
    user = test_db.query(User).first()
    token = generate_access_token(data={"sub": user.email})
    return f"Bearer {token}"

def test_create_comment(client, auth_token):
    comment_data = {
        "comment": "This is a new test comment",
        "parent_id": None
    }

    response = client.post(
        "/movies/comments/1",  # Movie ID is 1
        json=comment_data,
        headers={"Authorization": auth_token}
    )

    assert response.status_code == 201
    assert response.json()["comment"] == "This is a new test comment"

def test_get_comments_by_movie(client, auth_token):
    response = client.get("/movies/comments/movie/1", headers={"Authorization": auth_token})
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) > 0
    assert comments[1]["comment"] == "This is a new test comment"

def test_get_comments_by_user(client, auth_token):
    response = client.get("/movies/comments/user/1", headers={"Authorization": auth_token})
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) > 0
    assert comments[0]["user_id"] == 1
