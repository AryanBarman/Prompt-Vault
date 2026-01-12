from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class PromptPermission(Base):
    __tablename__ = "prompt_permissions"

    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)  # owner | contributor | viewer
