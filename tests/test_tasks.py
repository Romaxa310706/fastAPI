import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app, get_db
from src.database import Base
from src.models import TaskDB

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_task():
    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": 1
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_get_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task_not_found():
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_update_task():
    create = client.post("/tasks/", json={
        "title": "To Update",
        "description": "Old desc",
        "status": "pending",
        "priority": 0
    })
    task_id = create.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Updated",
        "description": "New desc",
        "status": "done",
        "priority": 5
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


def test_delete_task():
    create = client.post("/tasks/", json={
        "title": "To Delete",
        "description": "desc",
        "status": "pending",
        "priority": 0
    })
    task_id = create.json()["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"
