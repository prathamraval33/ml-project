"""In-memory and Redis caching service with fallback."""

import json
import logging
from typing import Any, Optional

from backend.app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Hybrid cache with Redis support and in-memory dict fallback."""

    def __init__(self):
        self._memory_cache: dict[str, str] = {}
        self._redis_client = None
        self._redis_available = False

        # Attempt Redis connection if configured
        try:
            import redis
            client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
            client.ping()
            self._redis_client = client
            self._redis_available = True
            logger.info("Connected to Redis at %s", settings.REDIS_URL)
        except Exception as e:
            logger.info("Redis not reachable (%s); using in-memory caching fallback.", e)
            self._redis_available = False

    def get(self, key: str) -> Optional[Any]:
        """Retrieve item from cache."""
        try:
            if self._redis_available and self._redis_client:
                data = self._redis_client.get(key)
                if data:
                    return json.loads(data.decode("utf-8") if isinstance(data, bytes) else data)
            elif key in self._memory_cache:
                return json.loads(self._memory_cache[key])
        except Exception as e:
            logger.warning("Cache get error for key %s: %s", key, e)
        return None

    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> None:
        """Store item in cache."""
        try:
            serialized = json.dumps(value)
            if self._redis_available and self._redis_client:
                self._redis_client.setex(key, expire_seconds, serialized)
            else:
                self._memory_cache[key] = serialized
        except Exception as e:
            logger.warning("Cache set error for key %s: %s", key, e)


cache_service = CacheService()
