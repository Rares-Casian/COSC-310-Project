

import jwt
from datetime import datetime, timezone
from typing import List
from backend.authentication import utils
from backend.authentication.security_config import SECRET_KEY, ALGORITHM


def load_revoked_tokens() -> List[str]:
    """Return the list of revoked (blacklisted) tokens."""
    return utils.load_revoked_tokens()


def save_revoked_tokens(tokens: List[str]) -> None:
    """Persist the revoked tokens list."""
    utils.save_revoked_tokens(tokens)


def cleanup_revoked_tokens() -> None:
    """Remove expired tokens from the revocation list to prevent unbounded growth."""
    tokens = load_revoked_tokens()
    active_tokens = []

    for token in tokens:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if exp > datetime.now(timezone.utc):
                active_tokens.append(token)
        except jwt.ExpiredSignatureError:
            continue
        except Exception:
            continue

    save_revoked_tokens(active_tokens)


def revoke_token(token: str) -> None:
    """Add a token to the revocation list."""
    cleanup_revoked_tokens()
    tokens = load_revoked_tokens()
    if token not in tokens:
        tokens.append(token)
        save_revoked_tokens(tokens)


def is_token_revoked(token: str) -> bool:
    """Return True if a token has been revoked."""
    tokens = load_revoked_tokens()
    return token in tokens
