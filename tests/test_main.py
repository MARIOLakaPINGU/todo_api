import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def clear_state():
    # Reset in-memory DB before each test
    main.todos.clear()

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_list_empty():
    res = client.get("/todos")
    assert res.status_code == 200
    assert res.json() == []

def test_create_and_get():
    res = client.post("/todos", json={"title": "Test Task", "description": "pytest"})
    assert res.status_code == 201
    created = res.json()
    assert created["title"] == "Test Task"
    assert created["completed"] is False
    todo_id = created["id"]

    res2 = client.get(f"/todos/{todo_id}")
    assert res2.status_code == 200
    assert res2.json()["id"] == todo_id

def test_update():
    created = client.post("/todos", json={"title": "A"}).json()
    todo_id = created["id"]

    res = client.put(f"/todos/{todo_id}", json={"completed": True, "title": "A+"})
    assert res.status_code == 200
    updated = res.json()
    assert updated["completed"] is True
    assert updated["title"] == "A+"

def test_delete():
    created = client.post("/todos", json={"title": "Will remove"}).json()
    todo_id = created["id"]

    res = client.delete(f"/todos/{todo_id}")
    assert res.status_code == 204
    assert res.content == b""

    res2 = client.get(f"/todos/{todo_id}")
    assert res2.status_code == 404

def test_validation_rejects_blank_title():
    res = client.post("/todos", json={"title": ""})
    assert res.status_code == 422  # Pydantic validation error

def test_openapi_present():
    res = client.get("/openapi.json")
    assert res.status_code == 200
    data = res.json()
    assert data["info"]["title"] == "To-Do List API"
