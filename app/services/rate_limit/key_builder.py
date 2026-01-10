from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM

def get_rate_limit_key(request, category):
    """
    Build rate limit key based on user email (if authenticated) or IP address.
    Does NOT raise exceptions - silently falls back to IP-based limiting.
    """
    client_ip = request.client.host
    auth_header = request.headers.get("Authorization")

    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    user_identifier = None
    if token:
        try:
            # Decode JWT directly without using the dependency function
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_identifier = payload.get("sub")  # email
        except JWTError:
            # Invalid/expired token - fall back to IP-based limiting
            user_identifier = None

    if user_identifier:
        return f"rate:{category}:user:{user_identifier}"
    return f"rate:{category}:ip:{client_ip}"
