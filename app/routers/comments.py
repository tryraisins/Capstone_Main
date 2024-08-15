from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.logger import custom_logger
from app.auth import get_current_user
import app.schemas as schemas
from app.crud import comment_crud_service, movie_crud_service, user_service
from sqlalchemy.orm import Session
from app.database import get_database_session

comment_routes = APIRouter()


@comment_routes.get("/", status_code=200, response_model=List[schemas.CommentResponse])
async def get_comments(db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    comments = comment_crud_service.get_comments(
        db,
        offset=offset,
        limit=limit
    )

    # Return a response that contains the comment, author and no. of replies
    response = [
        {
            "id": comment.id,
            "user_id": comment.user_id,
            "movie_id": comment.movie_id,
            "comment": comment.comment,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at,
            "author": {
                "id": author.id,
                "username": author.username,
                "email": author.email,
            },
            "replies": replies
        }
        for comment, author, replies in comments  # Unpack the query results
    ]

    return response


@comment_routes.get("/{comment_id}", status_code=200, response_model=schemas.CommentOut)
async def get_comment_by_id(comment_id: int, db: Session = Depends(get_database_session)):
    comment = comment_crud_service.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@comment_routes.get("/movie/{movie_id}", status_code=200, response_model=List[schemas.Comment])
async def get_comments_by_movie(movie_id: int, db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Movie Found")
    comments = comment_crud_service.get_comments_by_movie(
        db, movie_id, offset=offset, limit=limit)
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No comments for movie")
    return comments


@comment_routes.get("/user/{user_id}", status_code=200, response_model=List[schemas.Comment])
async def get_comments_by_user(user_id: int, db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    comment = comment_crud_service.get_comments_by_user(
        db, user_id, offset=offset, limit=limit)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No comments for user")
    return comment


@comment_routes.get("/replies/{parent_id}", status_code=200, response_model=List[schemas.Comment])
async def get_replies_to_comment(parent_id: int, db: Session = Depends(get_database_session), offset: int = 0, limit: int = 10):
    # Check if parent comment exists
    parent_comment = comment_crud_service.get_a_comment(db, parent_id)
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parent comment not found"
        )

    # Fetch replies
    replies = comment_crud_service.get_replies_to_comment(
        db, parent_id, offset=offset, limit=limit
    )

    if not replies:
        custom_logger.warning("No replies for comment....")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No replies found for this comment"
        )

    return replies


@comment_routes.post("/{movie_id}", status_code=201, response_model=schemas.Comment)
async def create_comment(movie_id: int, comment: schemas.CommentCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    movie = movie_crud_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Movie Found")

    db_comment = comment_crud_service.create_comment(
        db, comment=comment, user_id=current_user.id, movie_id=movie_id)

    return db_comment


@comment_routes.post("/reply_comment/{comment_id}")
async def reply_comment(comment_id: int, comment_payload: schemas.CommentBase, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    parent_comment = comment_crud_service.get_a_comment(
        db, comment_id=comment_id)
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    reply = comment_crud_service.reply_comment(
        comment_id, db, comment=comment_payload, user_id=current_user.id)
    return reply


@comment_routes.put("/{comment_id}", status_code=200, response_model=schemas.Comment)
async def update_comment(comment_payload: schemas.CommentUpdate, comment_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    comment = comment_crud_service.get_a_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    update_comment = comment_crud_service.update_comment(
        db, comment_payload=comment_payload, comment_id=comment_id)
    return update_comment


@comment_routes.delete("/{comment_id}", status_code=200)
async def delete_comment(comment_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_database_session)):
    comment = comment_crud_service.get_a_comment(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    comment_crud_service.delete_comment(db, comment_id)

    return {"message": "Success"}