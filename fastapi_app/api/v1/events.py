from uuid import UUID
from fastapi import APIRouter, Depends, Query
from cache.redis_cache import RedisCacheClient
from repositories.event_repository import PostgresEventRepository
from schemas.event_schema import EventDetailSchema, PaginatedEventsSchema
from services.event_service import EventService

router = APIRouter(prefix="/api/v1", tags=["events"])


def get_event_service() -> EventService:
    repository = PostgresEventRepository()
    cache = RedisCacheClient()
    return EventService(repository=repository, cache=cache)


@router.get("/events/", response_model=PaginatedEventsSchema)
def list_events(
    q: str = "",
    sort: str = Query("date", pattern="^(date|price|capacity)$"),
    page: int = 1,
    page_size: int = 9,
    timezone: str = "UTC",
    service: EventService = Depends(get_event_service),
):
    return service.list_events(q=q, sort=sort, page=page, page_size=page_size, timezone=timezone)


@router.get("/events/search/")
def search_events(
    query: str,
    page: int = 1,
    page_size: int = 9,
    timezone: str = "UTC",
    service: EventService = Depends(get_event_service),
):
    return service.search_events(query=query, page=page, page_size=page_size, timezone=timezone)


@router.get("/events/{event_id}", response_model=EventDetailSchema)
def get_event(
    event_id: UUID,
    timezone: str = "UTC",
    service: EventService = Depends(get_event_service),
):
    return service.get_event(event_id=event_id, timezone=timezone)
