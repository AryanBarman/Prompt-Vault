from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_v1_router
from app.core.database import Base, engine
from app.models import User, Prompt, PromptVersion
from app.core.logging_config import logger
from app.core.error_handler import global_exception_handler, domain_error_handler
from app.core.domain_error import DomainError
from app.core.request_logging import RequestLoggingMiddleware
from app.core.config import IS_PROD

app = FastAPI(
    title="FastAPI Auth & Prompts",
    description="Authentication and Prompt Management API with Version Control",
    version="1.0.0"
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(DomainError, domain_error_handler)
app.add_middleware(RequestLoggingMiddleware)

if IS_PROD:
    origins = [
        "https://your-frontend-domain.com",
        # add more if needed
    ]
else:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_v1_router, prefix="/api/v1")

# Create database tables
Base.metadata.create_all(bind=engine) # later will remove this and use alembic migrations 

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to FastAPI Auth & Prompts API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown")
