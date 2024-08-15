import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_database_session, Base
from app.models import User, Movie, Rating
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


def test_create_rating(client, auth_token):
    rating_data = {
        "rating_value": 5
    }

    response = client.post(
        "/movies/ratings/1",  # Movie ID is 1
        json=rating_data,
        headers={"Authorization": auth_token}
    )

    assert response.status_code == 201
    assert response.json()["rating_value"] == 5


def test_get_ratings(client, auth_token):
    response = client.get("/movies/ratings/", headers={"Authorization": auth_token})
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) > 0
    assert ratings[0]["rating_value"] == 5


def test_get_rating_by_id(client, auth_token):
    response = client.get("/movies/ratings/1", headers={"Authorization": auth_token})
    assert response.status_code == 200
    rating = response.json()
    assert rating["rating_value"] == 5


def test_get_ratings_by_movie_id(client, auth_token):
    response = client.get("/movies/ratings/movie_id/1", headers={"Authorization": auth_token})
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) > 0
    assert ratings[0]["rating_value"] == 5


def test_get_movie_avg_rating(client, auth_token):
    response = client.get("/movies/ratings/average_rating/1", headers={"Authorization": auth_token})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "successful"
    assert data["data"]["avg_rating"] == 5


def test_update_rating(client, auth_token):
    updated_rating_data = {
        "rating_value": 4
    }

    response = client.put(
        "/movies/ratings/1",
        json=updated_rating_data,
        headers={"Authorization": auth_token}
    )

    assert response.status_code == 200
    assert response.json()["rating_value"] == 4


def test_delete_rating(client, auth_token):
    response = client.delete("/movies/ratings/1", headers={"Authorization": auth_token})
    assert response.status_code == 200
    assert response.json()["message"] == "Successf"
