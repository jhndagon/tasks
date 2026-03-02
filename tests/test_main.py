import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    import os

    os.environ["TURSO_DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ.pop("TURSO_AUTH_TOKEN", None)

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_healthcheck(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_crud_flow(client: TestClient):
    create_response = client.post("/tasks", json={"title": "Primera tarea"})
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Primera tarea"
    assert created["done"] is False
    task_id = created["id"]

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 1
    assert listed[0]["id"] == task_id

    update_response = client.put(f"/tasks/{task_id}", json={"done": True, "title": "Actualizada"})
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["done"] is True
    assert updated["title"] == "Actualizada"

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    missing_update_response = client.put(f"/tasks/{task_id}", json={"done": False})
    assert missing_update_response.status_code == 404
    assert missing_update_response.json()["detail"] == "Task not found"
