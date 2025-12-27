import time 
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import jwt, JWTError
from app.core.logging_config import logger
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.metrics import metrics


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        metrics.record_request()

        start_time = time.time()
        
        # Extract user from token (optional - won't fail if no auth)
        user_email = self._get_user_from_token(request)
        user_info = f" by {user_email}" if user_email else ""
        
        logger.info(f"→ {request.method} {request.url.path}{user_info}")

        response = await call_next(request)

        duration = (time.time() - start_time) * 1000  # ms
        metrics.record_response_time(duration)
        status = response.status_code
        logger.info(f"← {request.method} {request.url.path} [{status}] in {duration:.2f}ms")

        return response
    
    def _get_user_from_token(self, request: Request) -> str | None:
        """Extract user email from JWT token if present"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")  # user email
        except (JWTError, Exception):
            return None
