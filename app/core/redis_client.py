import redis 
from .config import REDIS_URL

try:
    redis_client = redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )
    # Test connection
    redis_client.ping()
except (redis.ConnectionError, redis.TimeoutError) as e:
    print(f"Warning: Redis connection failed: {e}")
    print("Rate limiting will be disabled")
    redis_client = None