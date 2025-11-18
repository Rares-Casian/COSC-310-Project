"""Centralized filesystem paths for JSON-backed storage."""
import os

# Root directories
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "data")

# Subdirectories
USERS_DIR = os.path.join(DATA_DIR, "users")
MOVIES_DIR = os.path.join(DATA_DIR, "movies")
REVIEWS_DIR = os.path.join(DATA_DIR, "reviews")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
PENALTIES_DIR = os.path.join(DATA_DIR, "penalties")

# Files
USERS_ACTIVE_FILE = os.path.join(USERS_DIR, "users_active.json")
USERS_INACTIVE_FILE = os.path.join(USERS_DIR, "users_inactive.json")
REVOKED_TOKENS_FILE = os.path.join(USERS_DIR, "revoked_tokens.json")
REPORTS_FILE = os.path.join(REPORTS_DIR, "reports.json")
PENALTIES_FILE = os.path.join(PENALTIES_DIR, "penalties.json")
