import psycopg
from psycopg.rows import dict_row
from core.config import get_settings


def get_connection():
    settings = get_settings()
    return psycopg.connect(settings.database_url, row_factory=dict_row)
