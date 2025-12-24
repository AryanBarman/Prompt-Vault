from fastapi import APIRouter, Depends
from app.api.v1.auth import router as auth_router
from app.api.v1.prompt import router as prompt_router
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas import UserOut
from app.core.domain_error import PromptNotFound

router = APIRouter()

router.include_router(auth_router, prefix="", tags=["Auth"])
router.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    return current_user