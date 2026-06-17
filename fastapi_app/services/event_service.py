import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from fastapi import HTTPException
from cache.base import CacheClientProtocol
from core.config import get_settings
from repositories.base import EventRepositoryProtocol


class EventService:
    def __init__(self, repository: EventRepositoryProtocol, cache: CacheClientProtocol):
        self.repository = repository
        self.cache = cache
        self.settings = get_settings()

    def list_events(self, q: str, sort: str, page: int, page_size: int, timezone: str) -> dict:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 50)
        cache_key = f"events:list:q={q}:sort={sort}:page={page}:page_size={page_size}:tz={timezone}"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        count, rows = self.repository.list_events(q=q, sort=sort, page=page, page_size=page_size)
        response = {
            "count": count,
            "page": page,
            "page_size": page_size,
            "results": [self._to_event_list_item(row, timezone) for row in rows],
        }
        self.cache.set(cache_key, json.dumps(response, default=str), self.settings.cache_ttl_seconds)
        return response

    def get_event(self, event_id: UUID, timezone: str) -> dict:
        cache_key = f"events:detail:{event_id}:tz={timezone}"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached)

        row = self.repository.get_event_detail(event_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Event not found")

        response = self._to_event_detail(row, timezone)
        self.cache.set(cache_key, json.dumps(response, default=str), self.settings.cache_ttl_seconds * 2)
        return response

    def search_events(self, query: str, page: int, page_size: int, timezone: str) -> dict:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 50)
        count, rows = self.repository.search_events(query=query, page=page, page_size=page_size)
        return {
            "query": query,
            "count": count,
            "page": page,
            "page_size": page_size,
            "results": [self._to_event_list_item(row, timezone) for row in rows],
        }

    def _to_event_list_item(self, row: dict, timezone_name: str) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "description": row.get("description"),
            "starts_at": self._datetime_to_timezone(row["starts_at"], timezone_name),
            "venue": {
                "name": row["venue_name"],
                "city": row["venue_city"],
            },
            "min_price": self._decimal_to_float(row["min_price"]),
            "available": int(row["available"]),
            "total_capacity": int(row["total_capacity"]),
        }

    def _to_event_detail(self, row: dict, timezone_name: str) -> dict:
        item = self._to_event_list_item(row, timezone_name)
        item["ends_at"] = self._datetime_to_timezone(row["ends_at"], timezone_name)
        item["tiers"] = [
            {
                "id": tier["id"],
                "name": tier["name"],
                "price": self._decimal_to_float(tier["price"]),
                "capacity": int(tier["capacity"]),
                "available": int(tier["available"]),
            }
            for tier in row.get("tiers", [])
        ]
        return item

    def _datetime_to_timezone(self, value: datetime, timezone_name: str) -> str:
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            tz = ZoneInfo("UTC")
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        return value.astimezone(tz).isoformat()

    def _decimal_to_float(self, value: Decimal | int | float | None) -> float:
        if value is None:
            return 0.0
        return float(value)
