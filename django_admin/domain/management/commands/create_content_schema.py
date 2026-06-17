from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Creates the content schema if it does not exist."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS content;")

        self.stdout.write(self.style.SUCCESS("Schema content is ready."))