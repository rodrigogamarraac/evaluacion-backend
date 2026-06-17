from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from domain.models import Event, Order, Ticket, TicketType, Venue


class DomainModelTests(TestCase):
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Test Venue",
            city="Santa Cruz",
            address="Main street",
            capacity=1000,
        )
        self.event = Event.objects.create(
            venue=self.venue,
            title="Test Concert",
            description="Test description",
            starts_at=timezone.now() + timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1, hours=3),
        )
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name="General Admission",
            price="25.00",
            capacity=500,
        )
        self.order = Order.objects.create(
            buyer_name="Buyer",
            buyer_email="buyer@example.com",
        )

    def test_venue_uses_uuid_primary_key(self):
        self.assertIsNotNone(self.venue.id)
        self.assertEqual(len(str(self.venue.id)), 36)

    def test_event_belongs_to_venue(self):
        self.assertEqual(self.event.venue, self.venue)
        self.assertEqual(self.venue.events.count(), 1)

    def test_ticket_type_belongs_to_event(self):
        self.assertEqual(self.ticket_type.event, self.event)
        self.assertEqual(self.event.ticket_types.count(), 1)

    def test_order_can_have_many_tickets(self):
        Ticket.objects.create(order=self.order, ticket_type=self.ticket_type)
        Ticket.objects.create(order=self.order, ticket_type=self.ticket_type)
        self.assertEqual(self.order.tickets.count(), 2)

    def test_timestamps_are_created(self):
        self.assertIsNotNone(self.event.created_at)
        self.assertIsNotNone(self.event.modified_at)
