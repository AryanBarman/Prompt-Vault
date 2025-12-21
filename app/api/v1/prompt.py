from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas import PromptCreate, PromptUpdate, PromptOut
from app.crud import (
    create_prompt,
    get_prompts_by_user,
    get_prompt_by_id,
    update_prompt,
    delete_prompt,
    search_user_prompts
)

router = APIRouter()

@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
def create_new_prompt(
    prompt: PromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new prompt for the authenticated user
    """
    new_prompt = create_prompt(db, prompt, current_user.id)
    return new_prompt

@router.get("/", response_model=List[PromptOut])
def get_all_prompts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all prompts for the authenticated user
    """
    prompts = get_prompts_by_user(db, current_user.id, skip, limit)
    return prompts

@router.get("/{prompt_id: int}", response_model=PromptOut)
def get_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific prompt by ID
    """
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Check if prompt belongs to current user
    if prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this prompt"
        )
    
    return prompt

@router.put("/{prompt_id: int}", response_model=PromptOut)
def update_existing_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a prompt
    """
    # Check if prompt exists
    existing_prompt = get_prompt_by_id(db, prompt_id)
    if not existing_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Check if prompt belongs to current user
    if existing_prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this prompt"
        )
    
    # Update prompt
    updated_prompt = update_prompt(db, prompt_id, prompt_update)
    return updated_prompt

@router.delete("/{prompt_id: int}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a prompt
    """
    # Check if prompt exists
    existing_prompt = get_prompt_by_id(db, prompt_id)
    if not existing_prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    # Check if prompt belongs to current user
    if existing_prompt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this prompt"
        )
    
    # Delete prompt
    delete_prompt(db, prompt_id)
    return None


@router.get("/search", response_model=List[PromptOut])
def search_prompts(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search prompts by title or description for the authenticated user
    """
    print(f"query: {query}")
    prompts = search_user_prompts(db, current_user.id, query, skip, limit)
    return prompts

