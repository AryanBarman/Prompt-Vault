from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User,Prompt
from app.crud import get_total_prompts, get_recent_prompts

router = APIRouter()

@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    total_prompts = get_total_prompts(db, user.id)
    recent_prompts = get_recent_prompts(db, user.id)
    last_updated = recent_prompts[0]["updated_at"] if recent_prompts and recent_prompts[0] else None
    
    return {
        "total_prompts": total_prompts,
        "last_updated": last_updated,
        "recent_prompts": recent_prompts,
    }