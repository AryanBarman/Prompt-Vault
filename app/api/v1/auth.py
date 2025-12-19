from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import create_access_token
from app.schemas import UserCreate, UserOut, UserLogin, Token
from app.crud import get_user_by_email, create_user, authenticate_user

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    new_user = create_user(db, user)
    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to get access token
    """
    # Authenticate user
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
