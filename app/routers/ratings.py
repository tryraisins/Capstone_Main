from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.logger import custom_logger
import app.schemas as schemas
from app.crud import rating_crud_service, movie_crud_service
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.database import get_database_session

rating_routes = APIRouter()

@rating_routes.get("/", status_code=200, response_model=List[schemas.Rating])
async def get_ratings(db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    ratings = rating_crud_service.get_ratings(
        db,
        offset=offset,
        limit=limit
    )
    return ratings


@rating_routes.get("/{rating_id}", status_code=200, response_model=schemas.Rating)
async def get_rating_by_id(rating_id: int, db: Session = Depends(get_database_session)):
    rating = rating_crud_service.get_rating_by_id(
        db,
        rating_id=rating_id
    )
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@rating_routes.get("/movie_id/{movie_id}", status_code=200, response_model=List[schemas.Rating])
async def get_ratings_by_movie_id(movie_id: int, db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Movie Found")
    ratings = rating_crud_service.get_ratings_by_movie_id(
        db,
        movie_id=movie_id,
        offset=offset,
        limit=limit
    )
    return ratings

@rating_routes.get("/average_rating/{movie_id}", status_code=200)
async def get_movie_avg_rating(movie_id: int, db: Session = Depends(get_database_session)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Movie Found")
    avg_rating = rating_crud_service.aggregate_rating(db, movie_id)
    data = {
        "movie_id": movie.id,
        "movie_title": movie.title,
        "owner_id": movie.user_id,
        "avg_rating": avg_rating
    }

    return {"message": "successful", "data": data}


@rating_routes.post('/{movie_id}', status_code=201, response_model=schemas.Rating)
async def rate_movie(movie_id: int, rating: schemas.RatingCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Movie Found")
    # Query to see if there is an existing rating

    db_rating = rating_crud_service.get_rating(db, user_id=current_user.id, movie_id=movie_id)
    
    # Check if user has already rated movie
    if db_rating is not None:
        custom_logger.warning("User trying to rate an already rated movie...")
        raise HTTPException(status.HTTP_409_CONFLICT, detail="You have already rated movie. Update existing rating")

    new_rating = rating_crud_service.rate_movie_by_id(
        db,
        rating=rating,
        user_id=current_user.id,
        movie_id=movie_id
    )
    return new_rating


@rating_routes.put("/{rating_id}", status_code=200, response_model=schemas.Rating)
async def update_rating(rating_id: int, payload: schemas.RatingUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    rating = rating_crud_service.get_rating_by_id(db, rating_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
   
    update_rating = rating_crud_service.update_rating(db,rating_payload=payload, rating_id=rating_id)

    return update_rating


@rating_routes.delete("/{rating_id}", status_code=200)
async def delete_rating(rating_id: int, db: Session = Depends(get_database_session), current_user: schemas.User = Depends(get_current_user)):
    rating = rating_crud_service.get_rating_by_id(db, rating_id=rating_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if rating.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    rating_crud_service.delete_rating(db, rating_id=rating_id)
    return {"message": "Success"}