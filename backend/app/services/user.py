import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.base_models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
from datetime import datetime

logger = logging.getLogger(__name__)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    logger.debug(f"Looking up user by email: {email}")
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    logger.debug(f"Creating new user with email: {user.email}")
    try:
        hashed_password = get_password_hash(user.password)
        logger.debug("Password hashed successfully")
        
        db_user = User(
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        logger.debug("User object created")
        
        db.add(db_user)
        logger.debug("User added to session")
        
        try:
            db.commit()
            logger.debug("Database commit successful")
        except Exception as e:
            db.rollback()
            logger.error(f"Database commit failed: {str(e)}", exc_info=True)
            raise Exception(f"Database error: {str(e)}")
        
        db.refresh(db_user)
        logger.debug(f"User created successfully with ID: {db_user.id}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    logger.debug(f"Attempting to authenticate user: {email}")
    user = get_user_by_email(db, email)
    if not user:
        logger.warning(f"Authentication failed: User not found for email: {email}")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: Invalid password for email: {email}")
        return None
    logger.debug(f"Authentication successful for user: {email}")
    return user 