import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config.settings import settings


_lock = threading.Lock()
_backend_dir = Path(__file__).resolve().parents[2]
_log_dir = _backend_dir / "logs" / "ai_demo"
_log_file = _log_dir / "attendance_debug.jsonl"

# Backward-compatible mirror path (project root/logs) for easier discovery
_project_root = _backend_dir.parent
_legacy_log_dir = _project_root / "logs" / "ai_demo"
_legacy_log_file = _legacy_log_dir / "attendance_debug.jsonl"


def log_ai_demo_event(event: str, **payload: Any) -> None:
    if not settings.ai_demo_debug_log_enabled:
        return
    try:
        _log_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **payload,
        }
        line = json.dumps(record, ensure_ascii=False, default=str)
        with _lock:
            with _log_file.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
            if settings.ai_demo_debug_log_legacy_mirror:
                try:
                    _legacy_log_dir.mkdir(parents=True, exist_ok=True)
                    with _legacy_log_file.open("a", encoding="utf-8") as f2:
                        f2.write(line + "\n")
                except Exception:
                    pass
    except Exception:
        # never break runtime due to debug logging
        pass


def get_ai_demo_log_path() -> str:
    return str(_log_file)
