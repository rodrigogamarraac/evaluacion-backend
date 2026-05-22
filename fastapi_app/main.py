from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Event Ticketing Public API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.get("/api/v1/healthz")
def healthz():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "fastapi"
        }
    )


@app.get("/healthz")
def root_healthz():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "fastapi"
        }
    )


@app.get("/api/v1/events/")
def list_events(q: str = "", sort: str = "date", page: int = 1, page_size: int = 9):
    return {
        "count": 0,
        "page": page,
        "page_size": page_size,
        "results": []
    }


@app.get("/api/v1/events/search/")
def search_events(query: str):
    return {
        "query": query,
        "count": 0,
        "results": []
    }


@app.get("/api/v1/events/{event_id}")
def get_event(event_id: str):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Event not found"
        }
    )