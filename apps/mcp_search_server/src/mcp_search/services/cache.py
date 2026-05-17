import json
import hashlib

import redis.asyncio as redis

from mcp_search.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


def _make_key(prefix: str, value: str) -> str:
    """
    Create stable cache keys using hash to avoid huge keys.
    """
    digest = hashlib.sha256(value.encode()).hexdigest()
    return f"{prefix}:{digest}"


async def cache_extract_result(url: str, data: str, ttl: int = 3600) -> None:
    """
    Write a pre-serialized ExtractResponse to Redis.
    Designed to be scheduled with asyncio.create_task() from async callers
    so the caller never blocks on the cache write.

    Args:
        url:  The source URL (used to build the cache key).
        data: result.model_dump_json() — already-serialized JSON string.
        ttl:  Cache TTL in seconds (default 1 hour).
    """
    key = _make_key("extract", url)
    await redis_client.set(key, data, ex=ttl)