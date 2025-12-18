from pydantic import BaseModel

class PromptCreate(BaseModel):
    title: str
    content: str
    description: str | None = None

class PromptOut(BaseModel):
    id: int
    title: str
    content: str
    description: str | None
    user_id: int

    class Config:
        orm_mode = True
    