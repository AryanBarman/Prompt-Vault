from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate
from typing import List

def create_prompt(db: Session, prompt: PromptCreate, user_id: int) -> Prompt:
    """Create a new prompt"""
    db_prompt = Prompt(
        title=prompt.title,
        content=prompt.content,
        description=prompt.description,
        user_id=user_id
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def get_prompts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Prompt]:
    """Get all prompts for a user"""
    return db.query(Prompt).filter(Prompt.user_id == user_id).offset(skip).limit(limit).all()

def get_prompt_by_id(db: Session, prompt_id: int) -> Prompt | None:
    """Get a single prompt by ID"""
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()

def update_prompt(db: Session, prompt_id: int, prompt_update: PromptUpdate) -> Prompt | None:
    """Update a prompt"""
    db_prompt = get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        return None
    
    update_data = prompt_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prompt, field, value)
    
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def delete_prompt(db: Session, prompt_id: int) -> bool:
    """Delete a prompt"""
    db_prompt = get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        return False
    
    db.delete(db_prompt)
    db.commit()
    return True

def search_user_prompts(db: Session, user_id: int, query: str, skip: int = 0, limit: int = 100) -> List[Prompt]:
    """Search prompts by title or description for a specific user"""
    return db.query(Prompt).filter(Prompt.user_id == user_id, or_(Prompt.title.contains(query), Prompt.description.contains(query))).offset(skip).limit(limit).all()
