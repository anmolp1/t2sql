from datetime import timedelta
import logging
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token, verify_password
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema, UserResponse
from app.services.user import create_user, get_user_by_email

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(deps.get_db)):
    """Register a new user and return an access token."""
    logger.debug(f"Attempting to register user with email: {user.email}")
    try:
        # Check if user exists
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            logger.warning(f"Registration failed: Email {user.email} already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        logger.debug("Creating new user")
        db_user = create_user(db=db, user=user)
        logger.debug(f"User created with ID: {db_user.id}")
        
        # Generate access token
        access_token = create_access_token(subject=str(db_user.id))
        logger.debug("Access token generated successfully")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as he:
        logger.error(f"HTTP Exception during registration: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        ) 