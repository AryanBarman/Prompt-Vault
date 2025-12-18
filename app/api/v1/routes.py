from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from .auth import router as auth_router
from .prompt import router as prompt_router
from app.core.security import get_current_user

router = APIRouter()

router.include_router(auth_router, prefix="", tags=["Auth"])
router.include_router(prompt_router, prefix="/prompts", tags=["Prompts"])

@router.get("/profile")
def profile(user:str = Depends(get_current_user)):
    return {"email": user, "message": "Profile access granted"}