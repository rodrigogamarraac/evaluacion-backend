from typing import Optional, Protocol


class CacheClientProtocol(Protocol):
    def get(self, key: str) -> Optional[str]:
        ...

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        ...

    def ping(self) -> bool:
        ...
