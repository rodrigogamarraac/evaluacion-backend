from django.contrib import admin
from .models import Venue, Event, TicketType, Order, Ticket


class TicketTypeInline(admin.TabularInline):
    model = TicketType
    extra = 1
    fields = (
        "name",
        "price",
        "capacity",
        "sales_start",
        "sales_end",
    )


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    fields = (
        "ticket_type",
        "status",
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "capacity",
        "created_at",
        "modified_at",
    )
    search_fields = (
        "name",
        "city",
        "address",
    )
    list_filter = (
        "city",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "venue",
        "starts_at",
        "ends_at",
        "status",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "venue__name",
        "venue__city",
    )
    list_filter = (
        "status",
        "venue",
        "starts_at",
    )
    inlines = [
        TicketTypeInline,
    ]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event",
        "price",
        "capacity",
        "sales_start",
        "sales_end",
    )
    search_fields = (
        "name",
        "event__title",
    )
    list_filter = (
        "event",
        "price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "buyer_name",
        "buyer_email",
        "status",
        "created_at",
    )
    search_fields = (
        "buyer_name",
        "buyer_email",
    )
    list_filter = (
        "status",
        "created_at",
    )
    inlines = [
        TicketInline,
    ]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket_type",
        "order",
        "status",
        "created_at",
    )
    search_fields = (
        "ticket_type__name",
        "ticket_type__event__title",
        "order__buyer_name",
        "order__buyer_email",
    )
    list_filter = (
        "status",
        "ticket_type__event",
    )