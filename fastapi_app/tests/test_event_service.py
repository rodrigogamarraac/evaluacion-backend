from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
import pytest
from fastapi import HTTPException
from services.event_service import EventService


EVENT_ID = UUID("00000000-0000-0000-0000-000000000001")
TIER_ID = UUID("00000000-0000-0000-0000-000000000002")


class FakeCache:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ttl_seconds):
        self.store[key] = value

    def ping(self):
        return True


class BrokenCache(FakeCache):
    def get(self, key):
        return None

    def set(self, key, value, ttl_seconds):
        return None

    def ping(self):
        return False


class FakeRepository:
    def list_events(self, q, sort, page, page_size):
        return 1, [
            {
                "id": EVENT_ID,
                "title": "Rock Night",
                "description": "Live show",
                "starts_at": datetime(2026, 5, 22, 20, 0, tzinfo=timezone.utc),
                "venue_name": "LOUD Arena",
                "venue_city": "Santa Cruz",
                "min_price": Decimal("20.00"),
                "available": 450,
                "total_capacity": 500,
            }
        ]

    def get_event_detail(self, event_id):
        if event_id != EVENT_ID:
            return None
        return {
            "id": EVENT_ID,
            "title": "Rock Night",
            "description": "Live show",
            "starts_at": datetime(2026, 5, 22, 20, 0, tzinfo=timezone.utc),
            "ends_at": datetime(2026, 5, 22, 23, 0, tzinfo=timezone.utc),
            "venue_name": "LOUD Arena",
            "venue_city": "Santa Cruz",
            "min_price": Decimal("20.00"),
            "available": 450,
            "total_capacity": 500,
            "tiers": [
                {
                    "id": TIER_ID,
                    "name": "General Admission",
                    "price": Decimal("20.00"),
                    "capacity": 500,
                    "available": 450,
                }
            ],
        }

    def search_events(self, query, page, page_size):
        return self.list_events(q=query, sort="date", page=page, page_size=page_size)

    def ping(self):
        return True


def make_service(cache=None):
    return EventService(repository=FakeRepository(), cache=cache or FakeCache())


def test_list_events_returns_paginated_contract():
    data = make_service().list_events(q="rock", sort="date", page=1, page_size=9, timezone="UTC")
    assert data["count"] == 1
    assert data["page"] == 1
    assert data["results"][0]["title"] == "Rock Night"


def test_event_detail_returns_tiers():
    data = make_service().get_event(EVENT_ID, timezone="UTC")
    assert data["tiers"][0]["name"] == "General Admission"
    assert data["available"] == 450


def test_event_not_found_raises_404():
    with pytest.raises(HTTPException) as exc:
        make_service().get_event(UUID("00000000-0000-0000-0000-000000000099"), timezone="UTC")
    assert exc.value.status_code == 404


def test_service_gracefully_works_without_cache():
    data = make_service(cache=BrokenCache()).list_events(q="", sort="date", page=1, page_size=9, timezone="UTC")
    assert data["count"] == 1


def test_timezone_conversion_changes_offset():
    data = make_service().list_events(q="", sort="date", page=1, page_size=9, timezone="America/La_Paz")
    assert data["results"][0]["starts_at"].endswith("-04:00")
