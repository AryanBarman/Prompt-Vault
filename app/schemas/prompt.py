from pydantic import BaseModel, field_validator

class PromptCreate(BaseModel):
    title: str
    content: str
    description: str | None = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip()
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Content cannot be empty')
        return v.strip()

class PromptUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    description: str | None = None

class PromptOut(BaseModel):
    id: int
    title: str
    content: str
    description: str | None
    user_id: int

    class Config:
        from_attributes = True