from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class VenueSchema(BaseModel):
    name: str
    city: str


class TicketTierSchema(BaseModel):
    id: UUID
    name: str
    price: Decimal
    capacity: int
    available: int


class EventListItemSchema(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    starts_at: datetime
    venue: VenueSchema
    min_price: Decimal
    available: int
    total_capacity: int


class EventDetailSchema(EventListItemSchema):
    ends_at: datetime
    tiers: list[TicketTierSchema] = Field(default_factory=list)


class PaginatedEventsSchema(BaseModel):
    count: int
    page: int
    page_size: int
    results: list[EventListItemSchema]
