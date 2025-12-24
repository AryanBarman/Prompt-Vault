from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logging_config import logger
from app.core.domain_error import DomainError

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong. Please try again later."
        }
    )

async def domain_error_handler(request: Request, exc: DomainError):
    logger.warning(f"Domain error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message
        }
    )
