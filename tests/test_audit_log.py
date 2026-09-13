"""Tests for core.audit_log.AuditLog (structured JSON-Lines audit trail)."""
import json
import os

from core.audit_log import AuditLog


class TestAuditLog:
    def _read(self, path):
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def test_record_writes_jsonl_entry(self, tmp_path):
        p = os.path.join(tmp_path, "audit.jsonl")
        audit = AuditLog(p, actor="tester@host")
        audit.record("box_added", target="frame:3", cls="dog")
        rows = self._read(p)
        assert len(rows) == 1
        e = rows[0]
        assert e["action"] == "box_added"
        assert e["target"] == "frame:3"
        assert e["actor"] == "tester@host"
        assert e["details"]["cls"] == "dog"
        assert "ts" in e and e["ts"]

    def test_appends_not_overwrites(self, tmp_path):
        p = os.path.join(tmp_path, "audit.jsonl")
        audit = AuditLog(p, actor="t")
        audit.record("app_start")
        audit.record("annotations_saved", saved=5)
        audit.record("app_exit")
        rows = self._read(p)
        assert [r["action"] for r in rows] == ["app_start", "annotations_saved", "app_exit"]
        assert rows[1]["details"]["saved"] == 5

    def test_project_sink_mirrors(self, tmp_path):
        g = os.path.join(tmp_path, "global.jsonl")
        proj = os.path.join(tmp_path, "proj", "audit.jsonl")
        audit = AuditLog(g, actor="t")
        audit.set_project_sink(proj)
        audit.record("source_loaded", target="video.mp4", frames=100)
        assert self._read(g)[0]["action"] == "source_loaded"
        assert self._read(proj)[0]["details"]["frames"] == 100

    def test_default_actor_is_nonempty(self, tmp_path):
        audit = AuditLog(os.path.join(tmp_path, "a.jsonl"))
        assert isinstance(audit.actor, str) and audit.actor
