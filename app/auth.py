import os
import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.crud import user_service
from app.database import SessionLocal, get_database_session




# Load environment variables from .env file
load_dotenv()

# Retrieve configuration values
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "30"))

# Password hashing context
password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# OAuth2 password bearer scheme for token retrieval
def verify_password(plain_password, hashed_password):
    return password_hasher.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hasher.hash(password)

 # Authenticate a user based on credentials and password
def verify_user_credentials(db: Session, credentials: str, password: str):
    user = user_service.get_user_by_email_or_username(db, credentials)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def generate_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Session = Depends(get_database_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_service.get_user_by_email_or_username(db, username)
    if user is None:
        raise credentials_exception
    return user