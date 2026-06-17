import logging
from typing import Optional
import redis
from cache.base import CacheClientProtocol
from core.config import get_settings

logger = logging.getLogger(__name__)


class RedisCacheClient(CacheClientProtocol):
    def __init__(self):
        settings = get_settings()
        self._client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[str]:
        try:
            return self._client.get(key)
        except Exception as exc:
            logger.warning("redis_get_failed key=%s error=%s", key, exc)
            return None

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        try:
            self._client.setex(key, ttl_seconds, value)
        except Exception as exc:
            logger.warning("redis_set_failed key=%s error=%s", key, exc)

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception as exc:
            logger.warning("redis_ping_failed error=%s", exc)
            return False
