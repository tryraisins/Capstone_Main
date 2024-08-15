from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.logger import custom_logger
from app.auth import get_current_user
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.crud import movie_crud_service
from app.database import get_database_session

movie_routes = APIRouter()


# Endpoint to get a list of movies
@movie_routes.get("/", status_code=200, response_model=List[schemas.Movie])
async def get_movies(db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    movies = movie_crud_service.get_movies(
        db,
        offset=offset,
        limit=limit
    )
    return movies


# Endpoint to get a movie by its ID
@movie_routes.get("/{movie_id}", status_code=200, response_model=schemas.Movie)
async def get_movie_by_id(movie_id: str, db: Session = Depends(get_database_session)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        custom_logger.warning("Getting movie with wrong id....")
        raise HTTPException(detail="No Movie Found",
                            status_code=status.HTTP_404_NOT_FOUND)
    return movie


# Endpoint to get movies by genre
@movie_routes.get("/genre/{genre}", status_code=200, response_model=List[schemas.Movie])
async def get_movie_by_genre(genre: str, db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    movie = movie_crud_service.get_movie_by_genre(db, genre, offset, limit)
    if not movie:
        raise HTTPException(detail="No Movie Found",
                            status_code=status.HTTP_404_NOT_FOUND)
    return movie


# Endpoint to get movies by title
@movie_routes.get("/title/{movie_title}", status_code=200, response_model=List[schemas.Movie])
async def get_movie_by_title(movie_title: str, db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    movie = movie_crud_service.get_movie_by_title(db, movie_title, offset, limit)
    if not movie:
        custom_logger.info("Getting movie with wrong title...")
        raise HTTPException(detail="No Movie Found",
                            status_code=status.HTTP_404_NOT_FOUND)
    return movie


# Endpoint to create a new movie
@movie_routes.post('/', status_code=201, response_model=schemas.Movie)
async def list_movie(payload: schemas.MovieCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    movie = movie_crud_service.create_movie(
        db,
        payload,
        user_id=current_user.id
    )
    return movie


# Endpoint to update a movie by ID
@movie_routes.put('/{movie_id}', status_code=200, response_model=schemas.Movie)
async def update_movie(movie_id: int, payload: schemas.MovieUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    db_movie = movie_crud_service.get_movie_by_id(db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Movie Found")
    if db_movie.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    movie = movie_crud_service.update_movie(
        db, movie_id=movie_id, movie_payload=payload)
    return movie


# Endpoint to delete a movie by ID
@movie_routes.delete("/{movie_id}", status_code=200)
async def delete_movie(movie_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Movie Found")
    if movie.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    movie_crud_service.delete_movie(db, movie_id)

    return {"message": "Successf"}