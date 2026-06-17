from fastapi.testclient import TestClient
from main import app


def test_openapi_url_exists():
    client = TestClient(app)
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
