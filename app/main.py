from fastapi import FastAPI
from app.api.v1 import router as api_v1_router

app = FastAPI(title="FastAPI Auth", description="FastAPI Auth", version="1.0.0")

#include routes
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Auth"}