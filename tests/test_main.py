import pytest
from fastapi.testclient import TestClient


@pytest.fixture
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


def test_create_task_with_blank_title_returns_422(client: TestClient):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422
    assert "cannot be empty" in response.json()["detail"]


def test_list_tasks_can_filter_by_done(client: TestClient):
    first_response = client.post("/tasks", json={"title": "Tarea pendiente"})
    assert first_response.status_code == 201
    first_task = first_response.json()

    second_response = client.post("/tasks", json={"title": "Tarea completada"})
    assert second_response.status_code == 201
    second_task = second_response.json()

    update_response = client.put(f"/tasks/{second_task['id']}", json={"done": True})
    assert update_response.status_code == 200

    pending_response = client.get("/tasks?done=false")
    assert pending_response.status_code == 200
    pending = pending_response.json()
    assert [item["id"] for item in pending] == [first_task["id"]]

    completed_response = client.get("/tasks?done=true")
    assert completed_response.status_code == 200
    completed = completed_response.json()
    assert [item["id"] for item in completed] == [second_task["id"]]


def test_list_tasks_can_filter_by_title_contains(client: TestClient):
    first_response = client.post("/tasks", json={"title": "Comprar pan"})
    assert first_response.status_code == 201
    first_task = first_response.json()

    second_response = client.post("/tasks", json={"title": "Revisar correo"})
    assert second_response.status_code == 201
    second_task = second_response.json()

    third_response = client.post("/tasks", json={"title": "Lista de compras"})
    assert third_response.status_code == 201
    third_task = third_response.json()

    filtered_response = client.get("/tasks?title_contains=CoMPr")
    assert filtered_response.status_code == 200
    filtered = filtered_response.json()
    assert [item["id"] for item in filtered] == [first_task["id"], third_task["id"]]
    assert second_task["id"] not in [item["id"] for item in filtered]


def test_list_tasks_can_filter_by_title_starts_with(client: TestClient):
    first_response = client.post("/tasks", json={"title": "Comprar pan"})
    assert first_response.status_code == 201
    first_task = first_response.json()

    second_response = client.post("/tasks", json={"title": "Ir a comprar leche"})
    assert second_response.status_code == 201
    second_task = second_response.json()

    third_response = client.post("/tasks", json={"title": "Compilar reporte"})
    assert third_response.status_code == 201
    third_task = third_response.json()

    filtered_response = client.get("/tasks?title_starts_with=coMp")
    assert filtered_response.status_code == 200
    filtered = filtered_response.json()
    assert [item["id"] for item in filtered] == [first_task["id"], third_task["id"]]
    assert second_task["id"] not in [item["id"] for item in filtered]


def test_delete_missing_task_returns_404(client: TestClient):
    response = client.delete("/tasks/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
