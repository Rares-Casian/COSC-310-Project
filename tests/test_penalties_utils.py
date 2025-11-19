import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from backend.penalties import utils
from backend.penalties.schemas import Penalty


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def make_penalty(**overrides):
    base = {
        "penalty_id": "p1",
        "user_id": "u1",
        "type": "review_ban",      # valid PenaltyTypeEnum
        "severity": "low",         # VALID Severity enum
        "reason": "test",
        "issued_by": "mod1",
        "issued_at": datetime.utcnow(),
        "expires_at": None,
        "status": "active",
        "notes": None,
        "resolved_by": None,
        "resolved_at": None,
    }
    base.update(overrides)
    return Penalty(**base)


# ---------------------------------------------------------
# add_penalty
# ---------------------------------------------------------

@patch("backend.penalties.utils.save_json")
@patch("backend.penalties.utils.load_json")
@patch("backend.penalties.utils.user_utils.save_active_users")
@patch("backend.penalties.utils.user_utils.load_active_users")
def test_add_penalty_updates_json_and_user(
    mock_load_users, mock_save_users, mock_load, mock_save
):
    mock_load.return_value = []
    mock_load_users.return_value = [{"user_id": "u1"}]

    penalty = make_penalty()

    saved_penalty = utils.add_penalty(penalty)

    # JSON updated
    mock_save.assert_called_once()

    # User updated with penalty ID
    mock_save_users.assert_called_once()
    updated_users = mock_save_users.call_args[0][0]
    assert updated_users[0]["penalties"] == ["p1"]


# ---------------------------------------------------------
# get_penalties_for_user (no expiry)
# ---------------------------------------------------------

@patch("backend.penalties.utils.load_json")
def test_get_penalties_for_user_returns_only_matching(mock_load):
    mock_load.return_value = [
        {
            "penalty_id": "p1",
            "user_id": "u1",
            "type": "review_ban",
            "severity": "low",     # FIXED
            "reason": "x",
            "issued_by": "m",
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "status": "active",
            "notes": None,
            "resolved_by": None,
            "resolved_at": None,
        }
    ]

    res = utils.get_penalties_for_user("u1")
    assert len(res) == 1
    assert res[0].penalty_id == "p1"


# ---------------------------------------------------------
# get_penalties_for_user — expiration handling
# ---------------------------------------------------------

@patch("backend.penalties.utils._unlink_penalty_from_user")
@patch("backend.penalties.utils._save")
@patch("backend.penalties.utils._load")
def test_get_penalties_for_user_expires_old_penalties(mock_load, mock_save, mock_unlink):
    expired_time = (datetime.utcnow() - timedelta(days=1)).isoformat()

    mock_load.return_value = [
        {
            "penalty_id": "p1",
            "user_id": "u1",
            "type": "review_ban",
            "severity": "low",     # FIXED
            "reason": "x",
            "issued_by": "m",
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": expired_time,
            "status": "active",
            "notes": None,
            "resolved_by": None,
            "resolved_at": None,
        }
    ]

    res = utils.get_penalties_for_user("u1")

    assert res[0].status == "expired"
    mock_save.assert_called_once()
    mock_unlink.assert_called_once_with("u1", "p1")


# ---------------------------------------------------------
# resolve_penalty
# ---------------------------------------------------------

@patch("backend.penalties.utils._unlink_penalty_from_user")
@patch("backend.penalties.utils._save")
@patch("backend.penalties.utils._load")
def test_resolve_penalty_updates_fields(mock_load, mock_save, mock_unlink):
    mock_load.return_value = [
        {
            "penalty_id": "p1",
            "user_id": "u1",
            "status": "active",
            "type": "review_ban",
            "severity": "low",
            "reason": "",
            "issued_by": "m",
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": None,
            "notes": None,
            "resolved_by": None,
            "resolved_at": None,
        }
    ]

    utils.resolve_penalty("p1", moderator_id="mod123", notes="ok")

    saved = mock_save.call_args[0][0][0]
    assert saved["status"] == "resolved"
    assert saved["notes"] == "ok"
    assert saved["resolved_by"] == "mod123"
    assert "resolved_at" in saved
    mock_unlink.assert_called_once_with("u1", "p1")


# ---------------------------------------------------------
# delete_penalty
# ---------------------------------------------------------

@patch("backend.penalties.utils._unlink_penalty_from_user")
@patch("backend.penalties.utils._save")
@patch("backend.penalties.utils._load")
def test_delete_penalty_removes_penalty(mock_load, mock_save, mock_unlink):
    mock_load.return_value = [
        {"penalty_id": "p1", "user_id": "u1"},
        {"penalty_id": "p2", "user_id": "u2"},
    ]

    utils.delete_penalty("p1")

    saved_list = mock_save.call_args[0][0]
    assert len(saved_list) == 1
    assert saved_list[0]["penalty_id"] == "p2"
    mock_unlink.assert_called_once_with("u1", "p1")


# ---------------------------------------------------------
# check_active_penalty
# ---------------------------------------------------------

@patch("backend.penalties.utils._load")
def test_check_active_penalty_detects_block(mock_load):
    mock_load.return_value = [
        {"user_id": "u1", "type": "review_ban", "status": "active"}
    ]

    msg = utils.check_active_penalty("u1", ["review_ban"])
    assert msg == "User has an active review_ban penalty"


@patch("backend.penalties.utils._load")
def test_check_active_penalty_no_block(mock_load):
    mock_load.return_value = [
        {"user_id": "u1", "type": "posting_ban", "status": "expired"}
    ]
    msg = utils.check_active_penalty("u1", ["review_ban"])
    assert msg is None
