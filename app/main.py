from fastapi import FastAPI
from app.api.v1 import router as api_v1_router
from app.core.database import Base, engine
# Import models so SQLAlchemy knows about them
from app.models.user import User
from app.models.prompt import Prompt

app = FastAPI(title="FastAPI Auth", description="FastAPI Auth", version="1.0.0")

#include routes
app.include_router(api_v1_router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Auth"}