from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from sqlalchemy.orm import Session as DBSession
from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token, create_refresh_token
from app.schemas import UserCreate, UserOut, UserLogin, Token
from app.models.user import User
from app.crud import (
    get_user_by_email,
    create_user,
    authenticate_user,
    create_session,
    validate_and_refresh_session,
    revoke_session,
    revoke_session_by_token,
    revoke_all_user_sessions,
)


router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def signup(user: UserCreate, db: DBSession = Depends(get_db)):
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
def login(
    user: UserLogin, 
    response: Response,
    db: DBSession = Depends(get_db)
):
    """
    Login with email and password to get access token.
    Sets refresh token as HTTP-only cookie.
    """
    # Authenticate user
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token()
    
    # Create session
    create_session(db, db_user.id, refresh_token)

    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Only send over HTTPS in production
        samesite="strict",
        max_age=60*60*24*7  # 7 days
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_access_token(
    request: Request,
    response: Response,
    db: DBSession = Depends(get_db)
):
    """
    Refresh access token using refresh token from cookie.
    Implements refresh token rotation for security.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate session
    session, error = validate_and_refresh_session(db, refresh_token)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": session.user.email})
    new_refresh_token = create_refresh_token()
    
    # Revoke old session and create new one
    revoke_session(db, session)
    create_session(db, session.user_id, new_refresh_token)
    
    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60*60*24*7  # 7 days
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logout user by revoking session and clearing refresh token cookie.
    Revokes the session associated with the refresh token in the cookie.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        # Revoke the session for this refresh token
        revoke_session_by_token(db, refresh_token)
    
    # Clear the refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return {
        "message": "Logged out successfully"
    }
