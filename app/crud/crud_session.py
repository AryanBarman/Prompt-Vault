from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.core.security import hash_refresh_token

def create_session(db: DBSession, user_id: int, refresh_token: str) -> Session:
    """Create a new session for a user"""
    expires = datetime.utcnow() + timedelta(days=7)
    
    session = Session(
        user_id=user_id,
        refresh_token_hash=hash_refresh_token(refresh_token),
        expires_at=expires,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session

def get_session_by_refresh_token(db: DBSession, refresh_token: str) -> Session | None:
    """Get session by refresh token hash"""
    hashed = hash_refresh_token(refresh_token)
    return (
        db.query(Session)
        .filter(Session.refresh_token_hash == hashed)
        .first()
    )

def validate_and_refresh_session(
    db: DBSession, 
    refresh_token: str
) -> tuple[Session | None, str | None]:
    """
    Validate refresh token and return session with error message.
    Returns (session, error_message)
    """
    session = get_session_by_refresh_token(db, refresh_token)
    
    if not session:
        return None, "Invalid refresh token"
    
    if session.revoked:
        return None, "Session revoked"
    
    if session.expires_at < datetime.utcnow():
        return None, "Session expired"
    
    return session, None

def revoke_session(db: DBSession, session: Session) -> None:
    """Revoke a session"""
    session.revoked = True
    db.add(session)
    db.commit()

def revoke_session_by_token(db: DBSession, refresh_token: str) -> bool:
    """
    Revoke a specific session by refresh token.
    Returns True if session was found and revoked, False otherwise.
    """
    session = get_session_by_refresh_token(db, refresh_token)
    if session and not session.revoked:
        revoke_session(db, session)
        return True
    return False

def revoke_all_user_sessions(db: DBSession, user_id: int) -> int:
    """
    Revoke all active sessions for a user.
    Returns the number of sessions revoked.
    """
    active_sessions = (
        db.query(Session)
        .filter(Session.user_id == user_id, Session.revoked == False)
        .all()
    )
    
    count = len(active_sessions)
    for session in active_sessions:
        session.revoked = True
        db.add(session)
    
    db.commit()
    return count
