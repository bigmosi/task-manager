import pytest

USER_PAYLOAD = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "password123"
}

OTHER_USER_PAYLOAD = {
    "username": "otheruser",
    "email": "otheruser@example.com",
    "password": "password456"
}


@pytest.fixture(scope="module")
def registered_user(client):
    res = client.post("/users/", json=USER_PAYLOAD)
    assert res.status_code == 201
    return res.json()


@pytest.fixture(scope="module")
def auth_headers(client, registered_user):  # noqa: ARG001
    res = client.post("/auth/login", data={
        "username": USER_PAYLOAD["username"],
        "password": USER_PAYLOAD["password"]
    })
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def other_user(client):
    res = client.post("/users/", json=OTHER_USER_PAYLOAD)
    assert res.status_code == 201
    return res.json()


class TestRegisterUser:
    def test_success(self, client):
        res = client.post("/users/", json={
            "username": "reguser",
            "email": "reguser@example.com",
            "password": "password123"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == "reguser"
        assert data["email"] == "reguser@example.com"
        assert "password" not in data
        assert "id" in data
        assert data["is_active"] is True

    def test_duplicate_username(self, client):
        res = client.post("/users/", json={
            "username": "reguser",
            "email": "unique@example.com",
            "password": "password123"
        })
        assert res.status_code == 400

    def test_duplicate_email(self, client):
        res = client.post("/users/", json={
            "username": "uniqueuser",
            "email": "reguser@example.com",
            "password": "password123"
        })
        assert res.status_code == 400

    def test_invalid_email(self, client):
        res = client.post("/users/", json={
            "username": "validname",
            "email": "notanemail",
            "password": "password123"
        })
        assert res.status_code == 422

    def test_password_too_short(self, client):
        res = client.post("/users/", json={
            "username": "validname",
            "email": "valid@example.com",
            "password": "short"
        })
        assert res.status_code == 422

    def test_username_too_short(self, client):
        res = client.post("/users/", json={
            "username": "ab",
            "email": "ab@example.com",
            "password": "password123"
        })
        assert res.status_code == 422

    def test_username_too_long(self, client):
        res = client.post("/users/", json={
            "username": "a" * 21,
            "email": "long@example.com",
            "password": "password123"
        })
        assert res.status_code == 422


class TestGetUsers:
    def test_get_all_returns_list(self, client):
        res = client.get("/users/")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        assert len(res.json()) >= 1

    def test_limit_param(self, client):
        res = client.get("/users/?limit=1")
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_skip_beyond_total(self, client):
        res = client.get("/users/?skip=999999")
        assert res.status_code == 200
        assert res.json() == []


class TestGetUserById:
    def test_get_existing_user(self, client, registered_user):
        user_id = registered_user["id"]
        res = client.get(f"/users/{user_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == user_id
        assert data["username"] == registered_user["username"]
        assert data["email"] == registered_user["email"]

    def test_get_nonexistent_user(self, client):
        res = client.get("/users/999999")
        assert res.status_code == 404


class TestUpdateUser:
    def test_update_own_account(self, client, registered_user, auth_headers):
        user_id = registered_user["id"]
        res = client.put(
            f"/users/{user_id}",
            json={"username": "updated_testuser"},
            headers=auth_headers
        )
        assert res.status_code == 200
        assert res.json()["username"] == "updated_testuser"

    def test_update_another_user_forbidden(self, client, other_user, auth_headers):
        res = client.put(
            f"/users/{other_user['id']}",
            json={"username": "hacked"},
            headers=auth_headers
        )
        assert res.status_code == 403

    def test_update_unauthenticated(self, client, registered_user):
        user_id = registered_user["id"]
        res = client.put(f"/users/{user_id}", json={"username": "hacker"})
        assert res.status_code == 401


class TestDeleteUser:
    def test_delete_another_user_forbidden(self, client, other_user, auth_headers):
        res = client.delete(f"/users/{other_user['id']}", headers=auth_headers)
        assert res.status_code == 403

    def test_delete_unauthenticated(self, client, registered_user):
        user_id = registered_user["id"]
        res = client.delete(f"/users/{user_id}")
        assert res.status_code == 401

    def test_delete_own_account(self, client, registered_user, auth_headers):
        user_id = registered_user["id"]
        res = client.delete(f"/users/{user_id}", headers=auth_headers)
        assert res.status_code == 204
        assert client.get(f"/users/{user_id}").status_code == 404
