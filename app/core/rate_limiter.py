from app.services.rate_limit.policies import get_rate_limit_policy
from app.services.rate_limit.key_builder import get_rate_limit_key
from app.core.redis_client import redis_client
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        category, LIMIT, WINDOW = get_rate_limit_policy(request.url.path)
        key = get_rate_limit_key(request, category)

        requests_made = redis_client.incr(key)

        if requests_made == 1:
            redis_client.expire(key, WINDOW)

        if requests_made > LIMIT:
            ttl = redis_client.ttl(key)
            return JSONResponse(
                status_code=429,
                headers={
                    "Retry-After": str(ttl)
                },
                content={
                    "error":"rate limit exceeded",
                    "message": "Too many requests. Please slow down.",
                    "retry_after_seconds": ttl,
                    "limit": LIMIT,
                    "window_seconds": WINDOW
                }
            )

        return await call_next(request)
