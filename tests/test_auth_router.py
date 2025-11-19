from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.authentication import schemas

client = TestClient(app)

def test_register():
    payload = {
        "username": "alice123",
        "email": "alice@example.com",
        "password": "Password1!",
        "role": "member",
        "status": "active",
    }

    with patch("backend.authentication.router.utils.user_exists", return_value=(False, None)), \
         patch("backend.authentication.router.security.hash_password", return_value="hashed_pw"), \
         patch("backend.authentication.router.utils.add_user") as mock_add_user:

        res = client.post("/auth/register", json=payload)
        assert res.status_code == 201
        body = res.json()
        assert body["username"] == "alice123"
        assert body["email"] == "alice@example.com"
        assert body["role"] == "member"
        assert body["status"] == "active"

        mock_add_user.assert_called_once()

def test_login():
    user = {
        "user_id": "user123",
        "username": "alice123",
        "email": "alice@example.com",
        "hashed_password": "hashed_pw",
        "role": "member",
        "status": "active",
    }

    with patch("backend.authentication.router.utils.get_user_by_username_or_email", return_value=user), \
         patch("backend.authentication.router.security.verify_password", return_value=True), \
         patch("backend.authentication.router.security.create_access_token", return_value="access123"):

        res = client.post(
            "/auth/login",
            data={"username": "alice123", "password": "Password1!"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["access_token"] == "access123"
        assert body["token_type"] == "bearer"

def test_logout():
    with patch("backend.authentication.router.tokens.revoke_token") as mock_revoke:
        res = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer sometoken"},
        )
        assert res.status_code == 200
        assert res.json()["message"] == "Logged out successfully."
        mock_revoke.assert_called_once_with("sometoken")

def test_refresh_token():
    token_data = schemas.TokenData(user_id="user123", role="member", status="active")

    with patch("backend.authentication.router.security.get_current_user", return_value=token_data), \
         patch("backend.authentication.router.security.create_access_token", return_value="newtoken123"):

        res = client.post(
            "/auth/refresh",
            headers={"Authorization": "Bearer oldtoken"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["access_token"] == "newtoken123"
        assert body["token_type"] == "bearer"

def test_request_password_reset():
    users = [
        {
            "user_id": "user123",
            "email": "alice@example.com",
        }
    ]

    with patch("backend.authentication.router.utils.load_all_users", return_value=users), \
         patch("backend.authentication.router.security.create_reset_token", return_value="reset123"):

        res = client.post("/auth/password/request", params={"email": "alice@example.com"})
        assert res.status_code == 200
        body = res.json()
        assert body["reset_token"] == "reset123"
        assert "Use this token" in body["message"]

def test_reset_password():
    users = [
        {
            "user_id": "user123",
            "email": "alice@example.com",
            "status": "active",
            "hashed_password": "oldhash",
        }
    ]

    with patch("backend.authentication.router.security.verify_reset_token", return_value="user123"), \
         patch("backend.authentication.router.utils.load_all_users", return_value=users), \
         patch("backend.authentication.router.security.hash_password", return_value="newhash"), \
         patch("backend.authentication.router.utils.save_active_users") as mock_save_active, \
         patch("backend.authentication.router.utils.save_inactive_users") as mock_save_inactive:

        res = client.post(
            "/auth/password/reset",
            params={"token": "reset123", "new_password": "NewPassword1!"},
        )
        assert res.status_code == 200
        assert res.json()["message"] == "Password successfully reset"

        # All users are active in this setup
        mock_save_inactive.assert_called_once_with([])
        mock_save_active.assert_called_once()
        saved_active = mock_save_active.call_args[0][0]
        assert saved_active[0]["hashed_password"] == "newhash"

def test_read_current_user():
    fake_user = {
        "user_id": "user123",
        "username": "alice",
        "email": "alice@example.com",
        "role": "member",
        "status": "active",
    }

    with patch("backend.authentication.router.security.get_current_user", return_value=fake_user):
        res = client.get("/auth/me", headers={"Authorization": "Bearer sometoken"})
        assert res.status_code == 200
        body = res.json()
        assert body["user_id"] == "user123"
        assert body["username"] == "alice"
