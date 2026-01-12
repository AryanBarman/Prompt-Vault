from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.core.domain_error import PromptNotFound
from app.schemas import PromptCreate, PromptUpdate, PromptOut, PromptVersionOut, PromptAIRequest
from app.services.semantic_search_service import SemanticSearchService
from app.services.prompt_ai_service import PromptAIService
from app.models.prompt import Prompt
from app.crud import (
    create_prompt,
    get_prompts_by_user,
    get_prompt_by_id,
    update_prompt,
    delete_prompt,
    search_user_prompts,
    get_prompt_versions,
    rollback_prompt_to_version,
    get_prompt_version_count,
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
    # need to send updated at as well with the response
    prompts = [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "description": p.description,
            "updated_at": p.updated_at
        }
        for p in prompts
    ]
    return prompts

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
    if not query.strip():
        return []
    
    prompts = search_user_prompts(db, current_user.id, query, skip, limit)
    return prompts

@router.get("/{prompt_id}", response_model=PromptOut)
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
        raise PromptNotFound(prompt_id)
    
    # Check if prompt belongs to current user
    if prompt.user_id != current_user.id:
        raise UnauthorizedActionError("access this prompt")
    
    return prompt

@router.put("/{prompt_id}", response_model=PromptOut)
def update_existing_prompt(
    prompt_id: int,
    prompt_update: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a prompt (creates a version if content is updated)
    """
    # Check if prompt exists
    existing_prompt = get_prompt_by_id(db, prompt_id)
    if not existing_prompt:
        raise PromptNotFound(prompt_id)
    
    # Check if prompt belongs to current user
    if existing_prompt.user_id != current_user.id:
        raise UnauthorizedActionError("update this prompt")
    
    # Update prompt (CRUD handles version creation)
    updated_prompt = update_prompt(db, prompt_id, prompt_update, current_user.id)
    return updated_prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        raise PromptNotFound(prompt_id)
    
    # Check if prompt belongs to current user (redundant with RBAC but kept for clarity)
    if existing_prompt.user_id != current_user.id:
        raise UnauthorizedActionError("delete this prompt")
    
    # Delete prompt (RBAC check happens in CRUD layer)
    delete_prompt(db, prompt_id, current_user.id)
    return None

@router.get("/{prompt_id}/versions", response_model=List[PromptVersionOut])
def get_versions(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all versions for a specific prompt
    """
    # Check if prompt exists and belongs to current user
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise PromptNotFound(prompt_id)
    
    if prompt.user_id != current_user.id:
        raise UnauthorizedActionError("access this prompt's versions")
    
    # Get versions using CRUD function
    versions = get_prompt_versions(db, prompt_id)
    return versions

@router.post("/{prompt_id}/rollback/{version_number}", response_model=PromptOut)
def rollback_to_version(
    prompt_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rollback a prompt to a specific version
    """
    # Check if prompt exists and belongs to current user
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise PromptNotFound(prompt_id)
    
    if prompt.user_id != current_user.id:
        raise UnauthorizedActionError("rollback this prompt")
    
    # Rollback using CRUD function (RBAC check happens in CRUD layer)
    rolled_back_prompt = rollback_prompt_to_version(db, prompt_id, version_number, current_user.id)
    
    if not rolled_back_prompt:
        raise VersionNotFound(version_number)
    
    return rolled_back_prompt

@router.get("/{prompt_id}/version_count")
def get_version_count(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the total number of versions for a prompt
    """
    # Check if prompt exists and belongs to current user
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise PromptNotFound(prompt_id)
    
    if prompt.user_id != current_user.id:
        raise UnauthorizedActionError("access this prompt")
    
    # Get count using CRUD function
    count = get_prompt_version_count(db, prompt_id)
    return {"total_versions": count}

@router.get("/search/semantic")
def semantic_search(q:str, db: Session = Depends(get_db)):
    service = SemanticSearchService(db)
    results = service.search_prompts(q)

    return [
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
        }
        for p in results
    ]

@router.get("/{prompt_id}/ai/suggest-version")
def suggest_prompt_version(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if not prompt:
        raise PromptNotFound(prompt_id)

    service = PromptAIService()
    suggestion = service.suggest_next_version(prompt.content)

    return {
        "prompt_id": prompt_id,
        "title": prompt.title,
        "ai_suggestion": suggestion
    }

@router.post("/{prompt_id}/ai")
def run_prompt_ai_action(
    prompt_id: int,
    payload: PromptAIRequest = Body(...),
    db: Session = Depends(get_db),
):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if not prompt: 
        raise PromptNotFound(prompt_id)

    service = PromptAIService()
    
    mode = payload.mode.lower()
    
    if mode == "improve":
        result = service.improve_prompt(prompt.content)
    
    elif mode == "summarize":
        result = service.summarize_prompt(prompt.content)
    
    elif mode == "rewrite":
        variations = service.generate_variations(prompt.content, count=3)
        result = variations[0] if variations and len(variations) > 0 else prompt.content
    
    else:
        raise ValueError("Invalid mode")
    
    return {
        "prompt_id": prompt_id,
        "title": prompt.title,
        "mode": mode,
        "result": result,
        "meta": {
            "source": "PromptAIService",
            "model": "groq"
        }
    }
    
    
    
    
