from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logging_config import logger
from app.core.domain_error import DomainError
from app.core.security import get_current_user_email, get_token

async def global_exception_handler(request: Request, exc: Exception):
    user = get_current_user_email(get_token(request))
    logger.error(
    f"InternalServerError at {request.method} {request.url.path}{user} "
    f"- {exc.__class__.__name__}: {exc}"
)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong. Please try again later."
        }
    )

async def domain_error_handler(request: Request, exc: DomainError):
    user = get_current_user_email(get_token(request))
    logger.warning(f"{exc.__class__.__name__} at {request.method}{request.url.path} by {user} -{exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message
        }
    )
