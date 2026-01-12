from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.prompt_permission import PromptPermission

def require_role(db: Session, user_id: int, prompt_id: int, allowed_roles: list[str]) -> None:
    """
    Check if user has required role for a prompt.
    Raises HTTPException if user doesn't have permission.
    """
    perm = (
        db.query(PromptPermission)
        .filter_by(user_id=user_id, prompt_id=prompt_id)
        .first()
    )

    if not perm or perm.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
        )
