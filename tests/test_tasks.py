def test_create_task(authorized_client):
    response = authorized_client.post("/tasks/", json={
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "priority": "high",
        "status": "todo"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["priority"] == "high"
    assert "id" in data

def test_get_all_tasks(authorized_client):
    response = authorized_client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_filter_tasks_by_status(authorized_client):
    response = authorized_client.get("/tasks/?status=todo")
    assert response.status_code == 200
    for task in response.json():
        assert task["status"] == "todo"

def test_filter_tasks_by_priority(authorized_client):
    response = authorized_client.get("/tasks/?priority=high")
    assert response.status_code == 200
    for task in response.json():
        assert task["priority"] == "high"

def test_search_tasks(authorized_client):
    authorized_client.post("/tasks/", json={
        "title": "Read Python book",
        "priority": "medium"
    })
    response = authorized_client.get("/tasks/?search=python")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_update_task(authorized_client):
    create = authorized_client.post("/tasks/", json={
        "title": "Old title",
        "priority": "low"
    })
    task_id = create.json()["id"]

    response = authorized_client.put(f"/tasks/{task_id}", json={
        "title": "New title",
        "status": "in_progress"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["status"] == "in_progress"

def test_delete_task(authorized_client):
    create = authorized_client.post("/tasks/", json={
        "title": "Task to delete",
        "priority": "low"
    })
    task_id = create.json()["id"]

    response = authorized_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    get = authorized_client.get(f"/tasks/{task_id}")
    assert get.status_code == 404

def test_get_task_unauthorized(client):
    response = client.get("/tasks/")
    assert response.status_code == 401

def test_create_task_invalid_title(authorized_client):
    response = authorized_client.post("/tasks/", json={
        "title": "A",   # too short — min 2 chars
        "priority": "low"
    })
    assert response.status_code == 422