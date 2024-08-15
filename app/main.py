from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.logger import custom_logger
from app.middleware import request_logger_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth import verify_user_credentials, generate_access_token, password_hasher
from app.crud import user_service
import app.schemas as dto
from app.database import engine, Base, get_database_session
from app.routers.users import user_router
from app.routers.comments import comment_routes
from app.routers.movies import movie_routes
from app.routers.ratings import rating_routes

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI()

# Add middleware for request logging
app.add_middleware(BaseHTTPMiddleware, dispatch=request_logger_middleware)
custom_logger.info('Starting CheckFlix API...')

# Default route
@app.get('/')
async def home():
    return {'message': 'Welcome to CheckFlix'}

# Register resource routers
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(comment_routes, prefix="/movies/comments", tags=["Comments"])
app.include_router(movie_routes, prefix="/movies", tags=["Movies"])
app.include_router(rating_routes, prefix="/movies/ratings", tags=["Ratings"])

# User registration endpoint
@app.post("/register/", status_code=201, response_model=dto.User)
async def register(new_user: dto.UserCreate, db_session: Session = Depends(get_database_session)):
    existing_user = user_service.get_user_by_email_or_username(db_session, credentials=new_user.username)
    encrypted_password = password_hasher.hash(new_user.password)
    
    if existing_user:
        custom_logger.warning("User registration attempt for an existing user.")
        raise HTTPException(status_code=400, detail="User is already registered")
    
    return user_service.create_user(db_session=db_session, user=new_user, hashed_password=encrypted_password)

# User login endpoint
@app.post("/login", status_code=200)
async def login(auth_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_database_session)):
    authenticated_user = verify_user_credentials(db_session, auth_data.username, auth_data.password)
    
    if not authenticated_user:
        custom_logger.warning("Failed login attempt with incorrect credentials.")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = generate_access_token(data={"sub": authenticated_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
