"""In-memory and Redis caching service with fallback."""

import json
import logging
import time
from collections import OrderedDict
from typing import Any, Optional

from backend.app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Hybrid cache with Redis support and TTL-aware bounded in-memory fallback."""

    def __init__(self, max_entries: int = 1000):
        # key -> (expire_at_timestamp, serialized_json)
        self._memory_cache: OrderedDict[str, tuple[float, str]] = OrderedDict()
        self._max_entries = max_entries
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
        """Retrieve item from cache with TTL validation."""
        try:
            if self._redis_available and self._redis_client:
                data = self._redis_client.get(key)
                if data:
                    return json.loads(data.decode("utf-8") if isinstance(data, bytes) else data)
            elif key in self._memory_cache:
                expire_at, serialized = self._memory_cache[key]
                if time.time() > expire_at:
                    # Expired, clean up
                    del self._memory_cache[key]
                    return None
                # Mark as recently used
                self._memory_cache.move_to_end(key)
                return json.loads(serialized)
        except Exception as e:
            logger.warning("Cache get error for key %s: %s", key, e)
        return None

    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> None:
        """Store item in cache with TTL and capacity bounds."""
        try:
            serialized = json.dumps(value)
            if self._redis_available and self._redis_client:
                self._redis_client.setex(key, expire_seconds, serialized)
            else:
                now = time.time()
                # Purge expired items
                expired_keys = [k for k, (exp, _) in self._memory_cache.items() if now > exp]
                for k in expired_keys:
                    self._memory_cache.pop(k, None)

                # If still at capacity, evict oldest entry
                if len(self._memory_cache) >= self._max_entries:
                    self._memory_cache.popitem(last=False)

                self._memory_cache[key] = (now + expire_seconds, serialized)
        except Exception as e:
            logger.warning("Cache set error for key %s: %s", key, e)


cache_service = CacheService()

