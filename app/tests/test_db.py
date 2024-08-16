import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import  Base
from app.models import User, Movie, Comment
import os

# Retrieve configuration values
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "30"))



# Set up in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Mock data: Create a user, a movie, and a comment
    user = User(id=1, username="john_42", email="testuser@example.com", full_name="John Doe", hashed_password="fakehashedpassword")
    movie = Movie(id=1, title="Test Movie", description="Test description", genre="Drama")

    db.add(user)
    db.add(movie)
    db.commit()

    # Add a comment to the movie
    comment = Comment(id=1, user_id=1, movie_id=1, comment="This is a test comment", parent_id=None)
    db.add(comment)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)
