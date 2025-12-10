from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from .auth import router as auth_router
from app.core.security import get_current_user

router = APIRouter()

router.include_router(auth_router, prefix="", tags=["Auth"])

@router.get("/profile")
def profile(user:str = Depends(get_current_user)):
    return {"email": user, "message": "Profile access granted"}