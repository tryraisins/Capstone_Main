from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth import get_current_user
from app.logger import custom_logger
import app.schemas as schemas
from app.crud import user_service
from sqlalchemy.orm import Session
import app.schemas as schemas
from app.database import get_database_session

user_router = APIRouter()

# Endpoint to get a list of users
@user_router.get("/", status_code=200, response_model=List[schemas.User])
async def get_users(db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    users = user_service.get_users(
        db,
        offset=offset,
        limit=limit
    )
    return users

# Endpoint to get a single user by ID
@user_router.get("/{user_id}", status_code=200, response_model=schemas.User)
async def get_user_by_id(user_id: str, db: Session = Depends(get_database_session)):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# Endpoint to get a single user by username
@user_router.get("/name/{username}", status_code=200, response_model=schemas.User)
async def get_user_by_username(username: str, db: Session = Depends(get_database_session)):
    user = user_service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user

# Endpoint to update a user by ID
@user_router.put("/{user_id}", status_code=200, response_model=schemas.User)
async def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_database_session), current_user: schemas.User = Depends(get_current_user)):
    db_user = user_service.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.id != current_user.id:
        custom_logger.warning("User not authorized....")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = user_service.update_user(db, user_id, payload)

    return user

# Endpoint to delete a user by ID
@user_router.delete("/{user_id}", status_code=200)
async def delete_user(user_id: int, db: Session = Depends(get_database_session), current_user: schemas.User = Depends(get_current_user)):
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_service.delete_user(db, user_id=user_id)

    return {"message": "Success"}