import os
import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from domain.models import Event, Order, Ticket, TicketType, Venue


class Command(BaseCommand):
    help = "Seeds venues, events, ticket types, orders, and tickets on first start."

    def handle(self, *args, **options):
        if Event.objects.exists():
            self.stdout.write(self.style.SUCCESS("Seed skipped: events already exist."))
            return

        event_count = int(os.getenv("SEED_EVENTS", "300"))
        tickets_per_event = int(os.getenv("SEED_TICKETS_PER_EVENT", "500"))

        cities = ["Santa Cruz", "La Paz", "Cochabamba", "Sucre", "Tarija"]
        venue_names = ["LOUD Arena", "Central Hall", "Night Garden", "Open Air Stadium", "Underground Club"]
        event_words = ["Rock", "Indie", "Jazz", "Pop", "Electronic", "Metal", "Acoustic", "Festival"]
        tier_names = [("Early Bird", Decimal("20.00")), ("General Admission", Decimal("35.00")), ("VIP", Decimal("90.00"))]

        with transaction.atomic():
            venues = []
            for i in range(15):
                venues.append(
                    Venue(
                        name=f"{venue_names[i % len(venue_names)]} {i + 1}",
                        city=cities[i % len(cities)],
                        address=f"Main Avenue {100 + i}",
                        capacity=1200,
                    )
                )
            Venue.objects.bulk_create(venues)
            venues = list(Venue.objects.all())

            now = timezone.now()
            events = []
            for i in range(event_count):
                start = now + timedelta(days=i % 180, hours=18 + (i % 5))
                events.append(
                    Event(
                        venue=venues[i % len(venues)],
                        title=f"{event_words[i % len(event_words)]} Night {i + 1}",
                        description=f"Live event number {i + 1} with multiple ticket tiers and real availability.",
                        starts_at=start,
                        ends_at=start + timedelta(hours=3),
                        status=Event.Status.PUBLISHED,
                    )
                )
            Event.objects.bulk_create(events)
            events = list(Event.objects.all().order_by("starts_at"))

            ticket_types = []
            for event in events:
                for name, price in tier_names:
                    ticket_types.append(
                        TicketType(
                            event=event,
                            name=name,
                            price=price + Decimal(random.randint(0, 20)),
                            capacity=350,
                            sales_start=now - timedelta(days=30),
                            sales_end=event.starts_at,
                        )
                    )
            TicketType.objects.bulk_create(ticket_types)

            ticket_types_by_event = {}
            for ticket_type in TicketType.objects.select_related("event"):
                ticket_types_by_event.setdefault(ticket_type.event_id, []).append(ticket_type)

            orders = [
                Order(
                    buyer_name=f"Seed Buyer {i + 1}",
                    buyer_email=f"buyer{i + 1}@example.com",
                    status=Order.Status.PAID,
                )
                for i in range(event_count)
            ]
            Order.objects.bulk_create(orders)
            orders = list(Order.objects.all().order_by("created_at"))

            total_tickets = 0
            for event_index, event in enumerate(events):
                event_ticket_types = ticket_types_by_event[event.id]
                order = orders[event_index]
                tickets = []
                for j in range(tickets_per_event):
                    tickets.append(
                        Ticket(
                            order=order,
                            ticket_type=event_ticket_types[j % len(event_ticket_types)],
                            status=Ticket.Status.ACTIVE,
                        )
                    )
                Ticket.objects.bulk_create(tickets, batch_size=1000)
                total_tickets += len(tickets)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {event_count} events, {len(venues)} venues, "
                f"{event_count * len(tier_names)} ticket types, {total_tickets} tickets."
            )
        )
