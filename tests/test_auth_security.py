import pytest
from unittest.mock import patch
from datetime import timedelta
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from backend.authentication import security, schemas

def test_hash_password():
    with patch("backend.authentication.security.pwd_context.hash") as mock_hash:
        mock_hash.return_value = "hashed_pw"
        result = security.hash_password("Password1!")
        assert result == "hashed_pw"
        mock_hash.assert_called_once_with("Password1!")

def test_verify_password():
    with patch("backend.authentication.security.pwd_context.verify") as mock_verify:
        mock_verify.return_value = True
        ok = security.verify_password("plain", "hashed")
        assert ok is True
        mock_verify.assert_called_once_with("plain", "hashed")

def test_create_access_token():
    with patch("backend.authentication.security.jwt.encode") as mock_encode:
        mock_encode.return_value = "jwt_token"
        token = security.create_access_token({"sub": "123"}, expires_delta=timedelta(minutes=5))
        assert token == "jwt_token"
        assert mock_encode.called

def test_verify_access_token_valid():
    with patch("backend.authentication.security.tokens.is_token_revoked", return_value=False), \
         patch("backend.authentication.security.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "123", "role": "member", "status": "active"}

        payload = security.verify_access_token("sometoken")
        assert payload is not None
        assert payload["sub"] == "123"


def test_verify_access_token_revoked():
    with patch("backend.authentication.security.tokens.is_token_revoked", return_value=True):
        payload = security.verify_access_token("sometoken")
        assert payload is None


def test_verify_access_token_expired():
    with patch("backend.authentication.security.tokens.is_token_revoked", return_value=False), \
         patch("backend.authentication.security.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError("expired")

        payload = security.verify_access_token("sometoken")
        assert payload is None

def test_create_reset_token():
    with patch("backend.authentication.security.jwt.encode") as mock_encode:
        mock_encode.return_value = "reset_token"
        token = security.create_reset_token("user123")
        assert token == "reset_token"
        assert mock_encode.called

def test_verify_reset_token_valid():
    with patch("backend.authentication.security.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user123", "scope": "password_reset"}
        user_id = security.verify_reset_token("reset_token")
        assert user_id == "user123"

def test_verify_reset_token_invalid_scope():
    with patch("backend.authentication.security.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user123", "scope": "wrong_scope"}
        user_id = security.verify_reset_token("reset_token")
        assert user_id is None

class DummyCredentials(HTTPAuthorizationCredentials):
    def __init__(self, token: str):
        super().__init__(scheme="Bearer", credentials=token)


@pytest.mark.asyncio
async def test_get_current_user():
    creds = DummyCredentials("validtoken")

    with patch("backend.authentication.security.verify_access_token") as mock_verify:
        mock_verify.return_value = {
            "sub": "user123",
            "role": "member",
            "status": schemas.UserStatus.ACTIVE.value,
        }

        user = await security.get_current_user(credentials=creds)
        assert isinstance(user, schemas.TokenData)
        assert user.user_id == "user123"
        assert user.role == "member"
        assert user.status == schemas.UserStatus.ACTIVE.value
