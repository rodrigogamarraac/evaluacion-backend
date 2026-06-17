import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="CREATE SCHEMA IF NOT EXISTS content;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="Venue",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=150)),
                ("city", models.CharField(max_length=100)),
                ("address", models.TextField()),
                ("capacity", models.PositiveIntegerField()),
            ],
            options={"db_table": '"content"."venue"', "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("buyer_name", models.CharField(max_length=150)),
                ("buyer_email", models.EmailField(max_length=254)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("cancelled", "Cancelled")], default="paid", max_length=20)),
            ],
            options={"db_table": '"content"."ticket_order"', "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("cancelled", "Cancelled")], default="published", max_length=20)),
                ("venue", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="events", to="domain.venue")),
            ],
            options={"db_table": '"content"."event"', "ordering": ["starts_at"]},
        ),
        migrations.CreateModel(
            name="TicketType",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("capacity", models.PositiveIntegerField()),
                ("sales_start", models.DateTimeField(blank=True, null=True)),
                ("sales_end", models.DateTimeField(blank=True, null=True)),
                ("event", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ticket_types", to="domain.event")),
            ],
            options={"db_table": '"content"."ticket_type"', "ordering": ["price"]},
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("active", "Active"), ("cancelled", "Cancelled"), ("used", "Used")], default="active", max_length=20)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tickets", to="domain.order")),
                ("ticket_type", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="tickets", to="domain.tickettype")),
            ],
            options={"db_table": '"content"."ticket"', "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="event", index=models.Index(fields=["starts_at"], name="content_eve_starts__e4ee3d_idx")),
        migrations.AddIndex(model_name="event", index=models.Index(fields=["status"], name="content_eve_status_1692dc_idx")),
        migrations.AddIndex(model_name="event", index=models.Index(fields=["title"], name="content_eve_title_69b9f5_idx")),
        migrations.AddIndex(model_name="tickettype", index=models.Index(fields=["event"], name="content_tic_event_i_7144b6_idx")),
        migrations.AddIndex(model_name="tickettype", index=models.Index(fields=["price"], name="content_tic_price_3838b1_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["status"], name="content_tic_status_c08d56_idx")),
        migrations.AddIndex(model_name="order", index=models.Index(fields=["buyer_email"], name="content_tic_buyer_e_719479_idx")),
        migrations.AddIndex(model_name="ticket", index=models.Index(fields=["status"], name="content_tic_status_f0d0ff_idx")),
        migrations.AddIndex(model_name="ticket", index=models.Index(fields=["ticket_type"], name="content_tic_ticket__1aa2f6_idx")),
    ]
