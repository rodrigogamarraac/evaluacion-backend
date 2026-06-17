import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.v1.events import router as events_router
from cache.redis_cache import RedisCacheClient
from repositories.event_repository import PostgresEventRepository

logging.basicConfig(level=logging.INFO, format="level=%(levelname)s module=%(name)s message=%(message)s")

app = FastAPI(
    title="Event Ticketing Public API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.include_router(events_router)


@app.get("/api/v1/healthz")
def healthz():
    repository = PostgresEventRepository()
    cache = RedisCacheClient()
    db_ok = repository.ping()
    redis_ok = cache.ping()
    status_code = 200 if db_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if db_ok else "error",
            "service": "fastapi",
            "dependencies": {
                "postgres": "ok" if db_ok else "error",
                "redis": "ok" if redis_ok else "degraded",
            },
        },
    )


@app.get("/healthz")
def root_healthz():
    return healthz()
