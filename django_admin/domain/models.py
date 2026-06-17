import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Venue(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.TextField()
    capacity = models.PositiveIntegerField()

    class Meta:
        db_table = '"content"."venue"'
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.city}"


class Event(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )

    class Meta:
        db_table = '"content"."event"'
        ordering = ["starts_at"]
        indexes = [
            models.Index(fields=["starts_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return self.title


class TicketType(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="ticket_types",
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    sales_start = models.DateTimeField(null=True, blank=True)
    sales_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = '"content"."ticket_type"'
        ordering = ["price"]
        indexes = [
            models.Index(fields=["event"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return f"{self.event.title} - {self.name}"


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PAID,
    )

    class Meta:
        db_table = '"content"."ticket_order"'
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["buyer_email"]),
        ]

    def __str__(self):
        return f"{self.buyer_name} - {self.status}"


class Ticket(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"
        USED = "used", "Used"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT,
        related_name="tickets",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        db_table = '"content"."ticket"'
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["ticket_type"]),
        ]

    def __str__(self):
        return f"{self.ticket_type.name} - {self.status}"
