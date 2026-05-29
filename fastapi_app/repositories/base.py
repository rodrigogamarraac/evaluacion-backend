from typing import Protocol
from uuid import UUID


class EventRepositoryProtocol(Protocol):
    def list_events(self, q: str, sort: str, page: int, page_size: int) -> tuple[int, list[dict]]:
        ...

    def get_event_detail(self, event_id: UUID) -> dict | None:
        ...

    def search_events(self, query: str, page: int, page_size: int) -> tuple[int, list[dict]]:
        ...

    def ping(self) -> bool:
        ...
