import pytest
from unittest.mock import patch
from backend.authentication import utils, schemas

def test_user_exists():
    mock_users = [
        {"user_id": "1", "username": "alice", "email": "alice@example.com"},
        {"user_id": "2", "username": "john", "email": "john@example.com"},
    ]
    with patch("backend.authentication.utils.load_all_users", return_value=mock_users):
        exists, msg = utils.user_exists("alice", "new@example.com")
        assert exists is True
        assert msg == "Username already taken"

        exists, msg = utils.user_exists("newuser", "john@example.com")
        assert exists is True
        assert msg == "Email already taken"

        exists, msg = utils.user_exists("newuser", "new@example.com")
        assert exists is False
        assert msg is None

def test_add_user():
    new_user = {"user_id": "3", "username": "new", "email": "new@example.com"}

    with patch("backend.authentication.utils.load_active_users", return_value=[]) as mock_load_active, \
         patch("backend.authentication.utils.save_active_users") as mock_save_active:

        utils.add_user(new_user, active=True)

        mock_load_active.assert_called_once()
        mock_save_active.assert_called_once()
        saved_list = mock_save_active.call_args[0][0]
        assert len(saved_list) == 1
        assert saved_list[0]["user_id"] == "3"

        assert "penalties" in saved_list[0]

def test_get_user_by_id():
    mock_users = [
        {"user_id": "1", "username": "alice"},
        {"user_id": "2", "username": "john"},
    ]

    with patch("backend.authentication.utils.load_all_users", return_value=mock_users):
        user = utils.get_user_by_id("1")
        assert user is not None
        assert user["username"] == "alice"

        user_none = utils.get_user_by_id("999")
        assert user_none is None


def test_get_user_by_username():
    mock_users = [
        {"user_id": "1", "username": "alice"},
        {"user_id": "2", "username": "john"},
    ]

    with patch("backend.authentication.utils.load_all_users", return_value=mock_users):
        user = utils.get_user_by_username("john")
        assert user is not None
        assert user["user_id"] == "2"

        user_none = utils.get_user_by_username("nobody")
        assert user_none is None

def test_update_user_status():
    user_active = {
        "user_id": "1",
        "username": "alice",
        "status": "active",
    }

    active_list = [user_active]
    inactive_list = []

    with patch("backend.authentication.utils.load_active_users", return_value=active_list), \
         patch("backend.authentication.utils.load_inactive_users", return_value=inactive_list), \
         patch("backend.authentication.utils.save_active_users") as mock_save_active, \
         patch("backend.authentication.utils.save_inactive_users") as mock_save_inactive:

        result = utils.update_user_status("1", schemas.UserStatus.INACTIVE)
        assert result is True

        mock_save_active.assert_called_once()
        saved_active = mock_save_active.call_args[0][0]
        assert saved_active == []

        mock_save_inactive.assert_called_once()
        saved_inactive = mock_save_inactive.call_args[0][0]
        assert len(saved_inactive) == 1
        assert saved_inactive[0]["user_id"] == "1"
        assert saved_inactive[0]["status"] == schemas.UserStatus.INACTIVE.value
