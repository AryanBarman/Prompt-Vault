from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app.core.database import SessionLocal
from app.core.security import get_current_user_email
from app.models.user import User

def get_db() -> Session:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email)
) -> User:
    """Get current authenticated user from database"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user