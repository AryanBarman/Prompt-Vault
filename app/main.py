from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_v1_router
from app.core.database import Base, engine
# Import models so SQLAlchemy knows about them
from app.models import User, Prompt

app = FastAPI(
    title="FastAPI Auth & Prompts",
    description="Authentication and Prompt Management API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_v1_router, prefix="/api/v1")

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "message": "Welcome to FastAPI Auth & Prompts API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}