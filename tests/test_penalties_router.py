import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.penalties.router import router
from backend.penalties import utils, schemas
from backend.authentication.security import get_current_user

app = FastAPI()
app.include_router(router)
client = TestClient(app)


# ----------------------------------------------------------------------
# Fake users
# ----------------------------------------------------------------------

class DummyUser:
    def __init__(self, user_id="admin123", role="administrator"):
        self.user_id = user_id
        self.role = role


@pytest.fixture
def admin_user():
    return DummyUser(role="administrator")


@pytest.fixture
def mod_user():
    return DummyUser(role="moderator")


@pytest.fixture
def member_user():
    return DummyUser(role="member")


# ----------------------------------------------------------------------
# Fake load/save
# ----------------------------------------------------------------------

@pytest.fixture
def fake_load(monkeypatch):
    data = [
        {
            "penalty_id": "p1",
            "user_id": "u1",
            "type": "review_ban",
            "severity": "low",
            "reason": "spam",
            "issued_by": "admin123",
            "issued_at": "2024-01-01T00:00:00",
            "expires_at": None,
            "status": "active",
            "notes": None,
            "resolved_by": None,
            "resolved_at": None,
        }
    ]

    monkeypatch.setattr(utils, "_load", lambda: data.copy())
    return data


# ----------------------------------------------------------------------
# Admin override
# ----------------------------------------------------------------------

@pytest.fixture
def override_admin(admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_mod(mod_user):
    app.dependency_overrides[get_current_user] = lambda: mod_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_member(member_user):
    app.dependency_overrides[get_current_user] = lambda: member_user
    yield
    app.dependency_overrides.clear()


# ----------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------

def test_list_all_penalties(override_admin, fake_load):
    res = client.get("/penalties/")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_my_penalties(override_member, fake_load, monkeypatch):
    monkeypatch.setattr(utils, "get_penalties_for_user",
                        lambda uid: [schemas.Penalty(**fake_load[0])])

    res = client.get("/penalties/me")
    assert res.status_code == 200
    assert res.json()[0]["user_id"] == "u1"


def test_get_user_penalties(override_mod, fake_load, monkeypatch):
    monkeypatch.setattr(utils, "get_penalties_for_user",
                        lambda uid: [schemas.Penalty(**fake_load[0])])

    res = client.get("/penalties/u1")
    assert res.status_code == 200
    assert res.json()[0]["penalty_id"] == "p1"


def test_issue_penalty(override_mod, monkeypatch):
    payload = {
        "user_id": "u1",
        "type": "review_ban",
        "severity": "low",
        "reason": "spammy behaviour",
        "duration_days": 5
    }

    monkeypatch.setattr(utils, "add_penalty", lambda p: p)

    res = client.post("/penalties/", json=payload)
    assert res.status_code == 200
    assert res.json()["user_id"] == "u1"


def test_resolve_penalty(override_mod, monkeypatch):
    captured = {}

    def fake_resolve(pid, moderator_id, notes):
        captured["pid"] = pid
        captured["notes"] = notes
        captured["mod"] = moderator_id

    monkeypatch.setattr(utils, "resolve_penalty", fake_resolve)

    res = client.patch("/penalties/p1?notes=done")
    assert res.status_code == 200
    assert captured["pid"] == "p1"
    assert captured["notes"] == "done"


def test_delete_penalty(override_admin, fake_load, monkeypatch):
    deleted = {}

    def fake_delete(pid):
        deleted["pid"] = pid

    monkeypatch.setattr(utils, "delete_penalty", fake_delete)

    res = client.delete("/penalties/p1")
    assert res.status_code == 200
    assert deleted["pid"] == "p1"
