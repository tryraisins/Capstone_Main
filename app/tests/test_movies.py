import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_database_session
from app.models import User
from app.auth import generate_access_token
from app.logger import custom_logger

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

@pytest.fixture(scope="module")
def setup_movies(client, auth_token):
    # Create some movies for testing
    movie_data = [
        {"title": "Action Man", "genre": "Action", "description": "One Man Army."},
        {"title": "Tree", "genre": "Drama", "description": "Grow like a tree."}
    ]
    for movie in movie_data:
        response = client.post("/movies/", json=movie, headers={"Authorization": auth_token})
        assert response.status_code == 201
    return movie_data

def test_get_movies(client, setup_movies):
    x = setup_movies
    # Test default pagination settings
    response = client.get("/movies/?offset=0&limit=10")
    assert response.status_code == 200
    movies = response.json()

   
    
    # Check that the number of movies matches the setup
    assert len(movies) == 3  # Since setup_movies adds 2 movies
    
    # Verify that the movies include the expected titles
    titles = [movie["title"] for movie in movies]
    assert "Action Man" in titles
    assert "Tree" in titles


def test_get_movie_by_id(client, setup_movies):
    response = client.get("/movies/2")
    assert response.status_code == 200
    movie = response.json()
    assert movie["title"] == "Action Man"

def test_get_movie_by_genre(client, setup_movies):
    response = client.get("/movies/genre/Action")
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) > 0
    assert movies[0]["genre"] == "Action"

def test_get_movie_by_title(client, setup_movies):
    response = client.get("/movies/title/Action Man")
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) > 0
    assert movies[0]["title"] == "Action Man"

def test_create_movie(client, auth_token):
    new_movie = {"title": "Superhero", "genre": "Action", "description": "Superpowers and action."}
    response = client.post("/movies/", json=new_movie, headers={"Authorization": auth_token})
    assert response.status_code == 201
    movie = response.json()
    assert movie["title"] == "Superhero"

def test_update_movie(client, setup_movies, auth_token):
    updated_movie = {"title": "Action Man Updated", "genre": "Action", "description": "Updated description."}
    response = client.put("/movies/2", json=updated_movie, headers={"Authorization": auth_token})
    assert response.status_code == 200
    movie = response.json()
    assert movie["title"] == "Action Man Updated"

def test_delete_movie(client, setup_movies, auth_token):
    response = client.delete("/movies/2", headers={"Authorization": auth_token})
    assert response.status_code == 200
    assert response.json() == {"message": "Success"}

    # Verify that the movie was deleted
    response = client.get("/movies/2")
    assert response.status_code == 404
