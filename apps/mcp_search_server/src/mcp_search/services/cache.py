import json
import hashlib

import redis.asyncio as redis

from mcp_search.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)


def _make_key(prefix: str, value: str) -> str:
    """
    Create stable cache keys using hash to avoid huge keys.
    """
    digest = hashlib.sha256(value.encode()).hexdigest()
    return f"{prefix}:{digest}"