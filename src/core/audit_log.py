"""
core/audit_log.py
──────────────────
Structured, append-only **audit trail** of user and system actions — distinct
from the diagnostic system log (utils/logger.py).

Each action is written as one JSON object per line (JSON Lines) with a UTC
timestamp, the actor (OS user@host), the action, an optional target, and
free-form details. Entries are also mirrored as a concise line into the system
log so both streams stay correlated.

Two sinks:
  • global   — logs/audit_YYYYMMDD.jsonl (always)
  • project  — <project labels dir>/audit.jsonl (when a project is open)
"""
from __future__ import annotations

import getpass
import json
import os
import socket
import threading
from datetime import UTC, datetime

from utils.logger import get_log_dir, get_logger

_log = get_logger("audit")


def _default_actor() -> str:
    """Best-effort 'user@host' identity for the person running the app."""
    try:
        user = getpass.getuser()
    except Exception:
        user = os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"
    try:
        host = socket.gethostname()
    except Exception:
        host = "?"
    return f"{user}@{host}"


class AuditLog:
    """Append-only JSON-Lines audit trail (thread-safe)."""

    def __init__(self, path: str, actor: str | None = None):
        self.path = path
        self.actor = actor or _default_actor()
        self._lock = threading.Lock()
        self._project_sink: str | None = None
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def set_project_sink(self, path: str | None) -> None:
        """Mirror entries into a per-project audit.jsonl (None to disable)."""
        self._project_sink = path
        if path:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
            except OSError:
                self._project_sink = None

    def record(self, action: str, target: str | None = None, **details) -> dict:
        """Append one audit entry to every active sink and mirror to the system log."""
        entry = {
            "ts":     datetime.now(UTC).astimezone().isoformat(timespec="seconds"),
            "actor":  self.actor,
            "action": action,
            "target": target,
            "details": details or {},
        }
        line = json.dumps(entry, ensure_ascii=False)
        with self._lock:
            for sink in (self.path, self._project_sink):
                if not sink:
                    continue
                try:
                    with open(sink, "a", encoding="utf-8") as fh:
                        fh.write(line + "\n")
                except OSError as exc:
                    _log.warning(f"audit write failed ({sink}): {exc}")

        tgt = f" [{target}]" if target else ""
        det = (" " + " ".join(f"{k}={v}" for k, v in details.items())) if details else ""
        _log.info(f"AUDIT {action}{tgt}{det}")
        return entry


_default: AuditLog | None = None


def get_audit_log() -> AuditLog:
    """Return the process-wide audit log (global daily JSONL sink)."""
    global _default
    if _default is None:
        day = datetime.now().strftime("%Y%m%d")
        _default = AuditLog(os.path.join(get_log_dir(), f"audit_{day}.jsonl"))
    return _default


def audit_log_path() -> str:
    """Path of the global audit JSONL file for the current day."""
    return get_audit_log().path
