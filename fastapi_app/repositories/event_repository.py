from uuid import UUID
from db.session import get_connection
from repositories.base import EventRepositoryProtocol


class PostgresEventRepository(EventRepositoryProtocol):
    _SORT_SQL = {
        "date": "e.starts_at ASC",
        "price": "min_price ASC NULLS LAST",
        "capacity": "available DESC",
    }

    def ping(self) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 AS ok")
                return cur.fetchone()["ok"] == 1

    def list_events(self, q: str, sort: str, page: int, page_size: int) -> tuple[int, list[dict]]:
        offset = (page - 1) * page_size
        sort_sql = self._SORT_SQL.get(sort, self._SORT_SQL["date"])
        search = f"%{q}%"

        where = "e.status = 'published'"
        params = []
        if q:
            where += " AND (e.title ILIKE %s OR e.description ILIKE %s OR v.name ILIKE %s OR v.city ILIKE %s)"
            params.extend([search, search, search, search])

        count_sql = f"""
            SELECT COUNT(*) AS count
            FROM content.event e
            JOIN content.venue v ON v.id = e.venue_id
            WHERE {where}
        """

        data_sql = f"""
            WITH event_inventory AS (
                SELECT
                    e.id,
                    e.title,
                    e.description,
                    e.starts_at,
                    v.name AS venue_name,
                    v.city AS venue_city,
                    COALESCE(MIN(tt.price), 0) AS min_price,
                    COALESCE(SUM(tt.capacity), 0) AS total_capacity,
                    COALESCE(COUNT(t.id) FILTER (
                        WHERE t.status = 'active' AND o.status = 'paid'
                    ), 0) AS sold
                FROM content.event e
                JOIN content.venue v ON v.id = e.venue_id
                LEFT JOIN content.ticket_type tt ON tt.event_id = e.id
                LEFT JOIN content.ticket t ON t.ticket_type_id = tt.id
                LEFT JOIN content.ticket_order o ON o.id = t.order_id
                WHERE {where}
                GROUP BY e.id, e.title, e.description, e.starts_at, v.name, v.city
            )
            SELECT
                id,
                title,
                description,
                starts_at,
                venue_name,
                venue_city,
                min_price,
                total_capacity,
                GREATEST(total_capacity - sold, 0) AS available
            FROM event_inventory e
            ORDER BY {sort_sql}
            LIMIT %s OFFSET %s
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(count_sql, params)
                count = cur.fetchone()["count"]
                cur.execute(data_sql, [*params, page_size, offset])
                rows = cur.fetchall()
        return count, rows

    def get_event_detail(self, event_id: UUID) -> dict | None:
        event_sql = """
            WITH event_inventory AS (
                SELECT
                    e.id,
                    e.title,
                    e.description,
                    e.starts_at,
                    e.ends_at,
                    v.name AS venue_name,
                    v.city AS venue_city,
                    COALESCE(MIN(tt.price), 0) AS min_price,
                    COALESCE(SUM(tt.capacity), 0) AS total_capacity,
                    COALESCE(COUNT(t.id) FILTER (
                        WHERE t.status = 'active' AND o.status = 'paid'
                    ), 0) AS sold
                FROM content.event e
                JOIN content.venue v ON v.id = e.venue_id
                LEFT JOIN content.ticket_type tt ON tt.event_id = e.id
                LEFT JOIN content.ticket t ON t.ticket_type_id = tt.id
                LEFT JOIN content.ticket_order o ON o.id = t.order_id
                WHERE e.id = %s AND e.status = 'published'
                GROUP BY e.id, e.title, e.description, e.starts_at, e.ends_at, v.name, v.city
            )
            SELECT
                id,
                title,
                description,
                starts_at,
                ends_at,
                venue_name,
                venue_city,
                min_price,
                total_capacity,
                GREATEST(total_capacity - sold, 0) AS available
            FROM event_inventory
        """
        tiers_sql = """
            SELECT
                tt.id,
                tt.name,
                tt.price,
                tt.capacity,
                GREATEST(
                    tt.capacity - COALESCE(COUNT(t.id) FILTER (
                        WHERE t.status = 'active' AND o.status = 'paid'
                    ), 0),
                    0
                ) AS available
            FROM content.ticket_type tt
            LEFT JOIN content.ticket t ON t.ticket_type_id = tt.id
            LEFT JOIN content.ticket_order o ON o.id = t.order_id
            WHERE tt.event_id = %s
            GROUP BY tt.id, tt.name, tt.price, tt.capacity
            ORDER BY tt.price ASC
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(event_sql, [event_id])
                event = cur.fetchone()
                if not event:
                    return None
                cur.execute(tiers_sql, [event_id])
                tiers = cur.fetchall()

        event["tiers"] = tiers
        return event

    def search_events(self, query: str, page: int, page_size: int) -> tuple[int, list[dict]]:
        return self.list_events(q=query, sort="date", page=page, page_size=page_size)
