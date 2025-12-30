from pydantic import BaseModel
from datetime import datetime

class PromptVersionCreate(BaseModel):
    content: str

class PromptVersionOut(BaseModel):
    id: int
    prompt_id: int
    version_number: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class PromptAIRequest(BaseModel):
    mode: str
    extra_context: str | None = None
