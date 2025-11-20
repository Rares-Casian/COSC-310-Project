# tests/users/test_router.py
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

    with patch("backend.users.router.get_current_user", return_value=mock_user), \
         patch("backend.users.router.utils.get_user_by_id", return_value=fake_user_data):

        response = client.get("/users/me")

    assert response.status_code == 200
    assert response.json()["user_id"] == "user123"


def test_get_my_profile_not_found(mock_user):
    with patch("backend.users.router.get_current_user", return_value=mock_user), \
         patch("backend.users.router.utils.get_user_by_id", return_value=None):

        response = client.get("/users/me")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."
