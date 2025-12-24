# FastAPI Prompt Vault - Architecture Documentation

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Architecture Pattern](#architecture-pattern)
- [Development Guidelines](#development-guidelines)
- [Adding New Features](#adding-new-features)
- [Code Examples](#code-examples)
- [Best Practices](#best-practices)

---

## Overview

**Prompt Vault** is a FastAPI application for managing prompts with authentication, version control, and full CRUD operations. The application follows **clean architecture principles** with clear separation of concerns across three layers.

### Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2

---

## Project Structure

```
app/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── routes.py          # Main router aggregator
│       ├── auth.py            # Authentication endpoints
│       └── prompt.py          # Prompt CRUD endpoints
├── core/
│   ├── config.py              # Configuration & environment variables
│   ├── database.py            # Database connection & session
│   ├── deps.py                # Dependency injection functions
│   └── security.py            # Security utilities (JWT, password hashing)
├── crud/
│   ├── __init__.py
│   ├── crud_user.py           # User database operations
│   └── crud_prompt.py         # Prompt database operations
├── models/
│   ├── __init__.py
│   ├── user.py                # User SQLAlchemy model
│   ├── prompt.py              # Prompt SQLAlchemy model
│   └── prompt_version.py      # PromptVersion SQLAlchemy model
├── schemas/
│   ├── __init__.py
│   ├── user.py                # User Pydantic schemas
│   ├── prompt.py              # Prompt Pydantic schemas
│   └── prompt_version.py      # PromptVersion Pydantic schemas
└── main.py                    # Application entry point
```

---

## Architecture Pattern

We follow a **3-layer architecture** for clean separation of concerns:

```
┌─────────────────────────────────────┐
│   API Layer (routes)                │
│   - HTTP request/response           │
│   - Validation & authorization      │
│   - Error handling                  │
└──────────────┬──────────────────────┘
               │ calls
┌──────────────▼──────────────────────┐
│   CRUD Layer (business logic)       │
│   - Database operations             │
│   - Business rules                  │
│   - Data transformations            │
└──────────────┬──────────────────────┘
               │ queries
┌──────────────▼──────────────────────┐
│   Model Layer (database schema)     │
│   - SQLAlchemy models               │
│   - Relationships                   │
│   - Constraints                     │
└─────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. **API Layer** (`app/api/v1/`)
- Define HTTP endpoints
- Handle request/response serialization
- Validate user ownership
- Return appropriate HTTP status codes
- **Should NOT**: Contain business logic or direct database queries

#### 2. **CRUD Layer** (`app/crud/`)
- Encapsulate all database operations
- Implement business logic
- Handle data transformations
- **Should NOT**: Know about HTTP or authentication details

#### 3. **Model Layer** (`app/models/`)
- Define database schema
- Specify relationships
- Set constraints and indexes
- **Should NOT**: Contain business logic

---

## Development Guidelines

### 1. **Adding a New Endpoint**

Follow this checklist for every new endpoint:

#### ✅ Step 1: Create CRUD Function
**File**: `app/crud/crud_<resource>.py`

```python
def operation_name(db: Session, ...) -> ReturnType:
    """Clear docstring explaining what this does"""
    # Database operations here
    return result
```

#### ✅ Step 2: Export CRUD Function
**File**: `app/crud/__init__.py`

```python
from .crud_resource import (
    operation_name,  # Add to imports
)

__all__ = [
    "operation_name",  # Add to exports
]
```

#### ✅ Step 3: Create Route Handler
**File**: `app/api/v1/<resource>.py`

```python
@router.method("/path", response_model=Schema)
def endpoint_name(
    # Path parameters
    # Query parameters
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear docstring for API documentation
    """
    # 1. Validate ownership (if needed)
    # 2. Call CRUD function
    # 3. Handle errors
    # 4. Return response
```

### 2. **Naming Conventions**

| Type | Convention | Example |
|------|------------|---------|
| **CRUD Functions** | `verb_resource` | `get_prompt_by_id`, `create_user` |
| **Route Handlers** | `verb_descriptive_name` | `get_all_prompts`, `rollback_to_version` |
| **Models** | `PascalCase` | `User`, `Prompt`, `PromptVersion` |
| **Schemas** | `PascalCase` + suffix | `UserCreate`, `PromptOut`, `PromptUpdate` |
| **Files** | `snake_case` | `crud_prompt.py`, `prompt_version.py` |

### 3. **Import Organization**

Always organize imports in this order:

```python
# 1. Standard library
from typing import List
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

# 3. Local application
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas import PromptCreate, PromptOut
from app.crud import create_prompt, get_prompt_by_id
```

### 4. **Error Handling**

Use appropriate HTTP status codes:

```python
# 404 - Resource not found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Prompt not found"
)

# 403 - Forbidden (ownership check)
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorized to access this resource"
)

# 400 - Bad request (validation error)
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input data"
)

# 401 - Unauthorized (authentication required)
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"}
)
```

---

## Adding New Features

### Example: Adding a "Favorite Prompts" Feature

#### Step 1: Update Model
**File**: `app/models/prompt.py`

```python
is_favorite = Column(Boolean, default=False)
```

#### Step 2: Update Schema
**File**: `app/schemas/prompt.py`

```python
class PromptOut(BaseModel):
    # ... existing fields
    is_favorite: bool
```

#### Step 3: Create CRUD Function
**File**: `app/crud/crud_prompt.py`

```python
def toggle_favorite(db: Session, prompt_id: int) -> Prompt | None:
    """Toggle favorite status of a prompt"""
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        return None
    
    prompt.is_favorite = not prompt.is_favorite
    db.commit()
    db.refresh(prompt)
    return prompt
```

#### Step 4: Export Function
**File**: `app/crud/__init__.py`

```python
from .crud_prompt import (
    # ... existing imports
    toggle_favorite,
)

__all__ = [
    # ... existing exports
    "toggle_favorite",
]
```

#### Step 5: Add Endpoint
**File**: `app/api/v1/prompt.py`

```python
@router.post("/{prompt_id}/favorite", response_model=PromptOut)
def toggle_prompt_favorite(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status of a prompt"""
    # Validate ownership
    prompt = get_prompt_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    if prompt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Toggle favorite
    updated_prompt = toggle_favorite(db, prompt_id)
    return updated_prompt
```

#### Step 6: Recreate Database
```bash
python recreate_db.py
```

---

## Code Examples

### ✅ Good Example (Following Architecture)

```python
# CRUD Layer
def get_user_prompts(db: Session, user_id: int) -> List[Prompt]:
    return db.query(Prompt).filter(Prompt.user_id == user_id).all()

# API Layer
@router.get("/", response_model=List[PromptOut])
def list_prompts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompts = get_user_prompts(db, current_user.id)
    return prompts
```

### ❌ Bad Example (Violating Architecture)

```python
# API Layer - DON'T DO THIS!
@router.get("/")
def list_prompts(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email)
):
    # ❌ Manual user query in route
    user = db.query(User).filter(User.email == email).first()
    
    # ❌ Direct database query in route
    prompts = db.query(Prompt).filter(Prompt.user_id == user.id).all()
    
    return prompts
```

---

## Best Practices

### 1. **Always Validate Ownership**

```python
# Check if resource exists
resource = get_resource_by_id(db, resource_id)
if not resource:
    raise HTTPException(status_code=404, detail="Not found")

# Check if user owns the resource
if resource.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

### 2. **Use Proper Dependencies**

```python
# ✅ Good - Returns User object
current_user: User = Depends(get_current_user)

# ❌ Bad - Only returns email string
email: str = Depends(get_current_user_email)
```

### 3. **Reuse Existing CRUD Functions**

```python
# ✅ Good - Reuse existing function
prompt = get_prompt_by_id(db, prompt_id)

# ❌ Bad - Duplicate query
prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
```

### 4. **Use Response Models**

```python
# ✅ Good - Proper response model
@router.get("/", response_model=List[PromptOut])
def list_prompts(...):
    return prompts

# ❌ Bad - No response model
@router.get("/")
def list_prompts(...):
    return {"prompts": prompts}
```

### 5. **Keep Functions Focused**

Each function should do **one thing** well:

```python
# ✅ Good - Single responsibility
def get_prompt_by_id(db: Session, prompt_id: int) -> Prompt | None:
    return db.query(Prompt).filter(Prompt.id == prompt_id).first()

# ❌ Bad - Multiple responsibilities
def get_and_validate_prompt(db, prompt_id, user_id):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt or prompt.user_id != user_id:
        raise HTTPException(...)
    return prompt
```

---

## Database Migrations

### Current Approach (Development)

We use `recreate_db.py` to drop and recreate all tables:

```bash
python recreate_db.py
```

**⚠️ Warning**: This deletes all data!

### Production Approach (Recommended)

For production, use **Alembic** for database migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add favorite field"

# Apply migration
alembic upgrade head
```

---

## Testing

### Manual Testing

Use the interactive API docs:
```
http://localhost:8000/docs
```

### Automated Testing (Future)

Recommended structure:

```
tests/
├── test_crud/
│   ├── test_crud_user.py
│   └── test_crud_prompt.py
├── test_api/
│   ├── test_auth.py
│   └── test_prompts.py
└── conftest.py
```

---

## Common Patterns

### Pattern 1: List Resources

```python
# CRUD
def get_resources_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Resource).filter(Resource.user_id == user_id).offset(skip).limit(limit).all()

# API
@router.get("/", response_model=List[ResourceOut])
def list_resources(skip: int = 0, limit: int = 100, ...):
    resources = get_resources_by_user(db, current_user.id, skip, limit)
    return resources
```

### Pattern 2: Get Single Resource

```python
# CRUD
def get_resource_by_id(db: Session, resource_id: int):
    return db.query(Resource).filter(Resource.id == resource_id).first()

# API
@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(resource_id: int, ...):
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")
    if resource.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return resource
```

### Pattern 3: Create Resource

```python
# CRUD
def create_resource(db: Session, data: ResourceCreate, user_id: int):
    db_resource = Resource(**data.model_dump(), user_id=user_id)
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

# API
@router.post("/", response_model=ResourceOut, status_code=201)
def create_new_resource(data: ResourceCreate, ...):
    resource = create_resource(db, data, current_user.id)
    return resource
```

### Pattern 4: Update Resource

```python
# CRUD
def update_resource(db: Session, resource_id: int, data: ResourceUpdate):
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    db.commit()
    db.refresh(resource)
    return resource

# API
@router.put("/{resource_id}", response_model=ResourceOut)
def update_existing_resource(resource_id: int, data: ResourceUpdate, ...):
    # Validate ownership first
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")
    if resource.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = update_resource(db, resource_id, data)
    return updated
```

### Pattern 5: Delete Resource

```python
# CRUD
def delete_resource(db: Session, resource_id: int) -> bool:
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        return False
    db.delete(resource)
    db.commit()
    return True

# API
@router.delete("/{resource_id}", status_code=204)
def delete_existing_resource(resource_id: int, ...):
    # Validate ownership first
    resource = get_resource_by_id(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")
    if resource.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    delete_resource(db, resource_id)
    return None
```

---

## Quick Reference

### File Locations for Common Tasks

| Task | File(s) |
|------|---------|
| Add new endpoint | `app/api/v1/<resource>.py` |
| Add database operation | `app/crud/crud_<resource>.py` |
| Add database table | `app/models/<resource>.py` |
| Add validation schema | `app/schemas/<resource>.py` |
| Add configuration | `app/core/config.py` |
| Add dependency | `app/core/deps.py` |
| Add security utility | `app/core/security.py` |

### Common Commands

```bash
# Run development server
uvicorn app.main:app --reload

# Recreate database (development only)
python recreate_db.py

# Check database schema
python check_schema.py

# Git workflow
git add .
git commit -m "descriptive message"
git push
```

---

## Summary

**Key Principles:**
1. ✅ **Separation of Concerns** - Keep layers independent
2. ✅ **Reusability** - Write functions that can be used anywhere
3. ✅ **Consistency** - Follow established patterns
4. ✅ **Validation** - Always check ownership and existence
5. ✅ **Documentation** - Write clear docstrings

**Remember**: When in doubt, look at existing code for similar functionality and follow the same pattern!

---

*Last Updated: 2025-12-23*
