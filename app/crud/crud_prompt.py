from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate
from typing import List
from app.models.prompt_version import PromptVersion
from datetime import datetime

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

    # Create version entry
    version = PromptVersion(
        prompt_id=db_prompt.id,
        version_number=1,
        content=prompt.content,
        user_id=user_id
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return db_prompt

def get_prompts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Prompt]:
    """Get all prompts for a user"""
    return db.query(Prompt).filter(Prompt.user_id == user_id).offset(skip).limit(limit).all()

def get_prompt_by_id(db: Session, prompt_id: int) -> Prompt | None:
    """Get a single prompt by ID"""
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()

def update_prompt(db: Session, prompt_id: int, prompt_update: PromptUpdate, user_id: int) -> Prompt | None:
    """Update a prompt and create a version entry"""
    db_prompt = get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        return None
    
    # Only create version if content is being updated
    if prompt_update.content is not None:
        # Get last version number
        last_version = (
            db.query(PromptVersion)
            .filter(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
            .first()
        )
        
        new_version_number = 1 if not last_version else last_version.version_number + 1
        
        # Create version entry
        version = PromptVersion(
            prompt_id=prompt_id,
            version_number=new_version_number,
            content=prompt_update.content,
            user_id=user_id
        )
        db.add(version)
    
    # Update prompt fields
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

def get_prompt_versions(db: Session, prompt_id: int) -> List:
    """Get all versions for a prompt, ordered by version number (newest first)"""
    
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
        .all()
    )

def rollback_prompt_to_version(db: Session, prompt_id: int, version_number: int) -> Prompt | None:
    """Rollback a prompt to a specific version"""
    # Get the prompt
    db_prompt = get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        return None
    
    # Get the version to rollback to
    version = (
        db.query(PromptVersion)
        .filter(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number == version_number
        )
        .first()
    )
    
    if not version:
        return None
    
    # Restore content from version
    db_prompt.content = version.content
    db_prompt.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

def get_prompt_version_count(db: Session, prompt_id: int) -> int:
    """Get the total number of versions for a prompt"""
    
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_id == prompt_id)
        .count()
    )
