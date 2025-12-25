import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import logger
from app.core.security import get_current_user_email

def _get_token(request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        user = get_current_user_email(_get_token(request))
        start_time = time.time()

        logger.info(f"Incoming request: {request.method} {request.url.path} from {user}")

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000  # ms
        logger.info(f"Completed request: {request.method} {request.url.path} in {duration:.2f}ms from {user}")

        return response
