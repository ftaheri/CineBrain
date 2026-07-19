from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_service():
    response = client.get("/movies/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1