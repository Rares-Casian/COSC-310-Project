# tests/users/test_routes.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.users.router import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)
