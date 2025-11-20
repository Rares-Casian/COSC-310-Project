# tests/users/test_routes.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.users.router import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


# ------------------------------------------------------------
# Helper mock user
# ------------------------------------------------------------
@pytest.fixture
def mock_user():
    return MagicMock(user_id="user123", role="user", email="test@example.com")


@pytest.fixture
def mock_admin():
    return MagicMock(user_id="admin123", role="administrator", email="admin@example.com")


# ------------------------------------------------------------
# GET /users/me
# ------------------------------------------------------------
def test_get_my_profile_success(mock_user):
    fake_user_data = {"user_id": "user123", "username": "John", "email": "john@example.com"}

    with patch("backend.users.routes.get_current_user", return_value=mock_user), \
         patch("backend.users.routes.utils.get_user_by_id", return_value=fake_user_data):

        response = client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["user_id"] == "user123"


def test_get_my_profile_not_found(mock_user):
    with patch("backend.users.routes.get_current_user", return_value=mock_user), \
         patch("backend.users.routes.utils.get_user_by_id", return_value=None):

        response = client.get("/users/me")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# ------------------------------------------------------------
# PATCH /users/me
# ------------------------------------------------------------
def test_update_my_profile_success(mock_user):
    update_data = {"username": "newname"}
    updated_user = {"user_id": mock_user.user_id, "username": "newname", "email": mock_user.email}

    with patch("backend.users.routes.get_current_user", return_value=mock_user), \
         patch("backend.users.routes.utils.update_user", return_value=updated_user):

        response = client.patch("/users/me", json=update_data)

    assert response.status_code == 200
    assert response.json()["username"] == "newname"


# ------------------------------------------------------------
# PATCH /users/me/password
# ------------------------------------------------------------
def test_change_my_password_success(mock_user):
    with patch("backend.users.routes.get_current_user", return_value=mock_user), \
         patch("backend.users.routes.utils.change_password", return_value=None):

        response = client.patch("/users/me/password",
                                json={"old_password": "old", "new_password": "new"})

    assert response.status_code == 200
    assert response.json() == {"message": "Password updated successfully."}


# ------------------------------------------------------------
# PATCH /users/me/status
# ------------------------------------------------------------
def test_change_my_status_success(mock_user):
    updated_user = {"user_id": mock_user.user_id, "status": "active"}

    with patch("backend.users.routes.get_current_user", return_value=mock_user), \
         patch("backend.users.routes.utils.update_user_status", return_value=updated_user):

        response = client.patch("/users/me/status", json={"status": "active"})

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_change_my_status_invalid_value(mock_user):
    with patch("backend.users.routes.get_current_user", return_value=mock_user):

        response = client.patch("/users/me/status", json={"status": "invalid"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status value."


# ------------------------------------------------------------
# GET /users/ (admin)
# ------------------------------------------------------------
def test_list_users_success(mock_admin):
    fake_users = [{"user_id": "u1"}, {"user_id": "u2"}]

    with patch("backend.users.routes.get_current_user", return_value=mock_admin), \
         patch("backend.users.routes.require_role", return_value=None), \
         patch("backend.users.routes.utils.load_active_users", return_value=fake_users):

        response = client.get("/users/")

    assert response.status_code == 200
    assert len(response.json()) == 2


# ------------------------------------------------------------
# GET /users/{user_id}
# ------------------------------------------------------------
def test_get_user_success(mock_admin):
    fake_user = {"user_id": "u1"}

    with patch("backend.users.routes.get_current_user", return_value=mock_admin), \
         patch("backend.users.routes.require_role", return_value=None), \
         patch("backend.users.routes.utils.get_user_by_id", return_value=fake_user):

        response = client.get("/users/u1")

    assert response.status_code == 200
    assert response.json()["user_id"] == "u1"


def test_get_user_not_found(mock_admin):
    with patch("backend.users.routes.get_current_user", return_value=mock_admin), \
         patch("backend.users.routes.require_role", return_value=None), \
         patch("backend.users.routes.utils.get_user_by_id", return_value=None):

        response = client.get("/users/u999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# ------------------------------------------------------------
# PATCH /users/{user_id}
# ------------------------------------------------------------
def test_update_user_admin_success(mock_admin):
    updated = {"user_id": "u1", "username": "changed"}

    with patch("backend.users.routes.get_current_user", return_value=mock_admin), \
         patch("backend.users.routes.require_role", return_value=None), \
         patch("backend.users.routes.utils.update_user", return_value=updated):

        response = client.patch("/users/u1", json={"username": "changed"})

    assert response.status_code == 200
    assert response.json()["username"] == "changed"


# ------------------------------------------------------------
# DELETE /users/{user_id}
# ------------------------------------------------------------
def test_delete_user_success(mock_admin):
    with patch("backend.users.routes.get_current_user", return_value=mock_admin), \
         patch("backend.users.routes.require_role", return_value=None), \
         patch("backend.users.routes.utils.delete_user", return_value=None):

        response = client.delete("/users/u1")

    assert response.status_code == 200
    assert response.json()["message"] == "User u1 deleted."