"""JSON I/O helpers with atomic writes and datetime-safe serialization."""
import json, os, tempfile, shutil
from datetime import datetime, date
from typing import Any, TypeVar

T = TypeVar("T")


def _to_jsonable(obj: Any) -> Any:
    """Recursively convert datetimes to ISO strings."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj


def ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def load_json(path: str, default: T) -> T:
    """Load JSON or return default if missing/invalid."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except json.JSONDecodeError:
        return default


def save_json(path: str, data: Any, *, atomic: bool = True) -> None:
    """Write JSON to disk atomically."""
    ensure_parent(path)
    payload = json.dumps(_to_jsonable(data), indent=4)
    if not atomic:
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)
        return
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path))
    os.close(tmp_fd)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(payload)
        shutil.move(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
