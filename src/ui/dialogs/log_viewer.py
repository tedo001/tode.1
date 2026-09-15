"""
ui/dialogs/log_viewer.py
─────────────────────────
Run-log viewer: tails the system log and the structured audit log, with
all / warn / error filters and copy-to-clipboard.
"""
from __future__ import annotations

import json
import os

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from core.audit_log import audit_log_path
from utils.logger import get_log_file_path


def _tail(path: str, limit: int = 400) -> list[str]:
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.readlines()[-limit:]
    except OSError:
        return []


class LogViewerDialog(QDialog):
    """Shows system + audit logs with level filtering."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run log")
        self.resize(760, 520)
        self._filter = "all"

        root = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Run log</b>"))
        header.addStretch(1)
        for name in ("all", "warn", "error"):
            b = QPushButton(name)
            b.setCheckable(True)
            b.setChecked(name == "all")
            b.clicked.connect(lambda _c=False, n=name: self._set_filter(n))
            header.addWidget(b)
            setattr(self, f"_btn_{name}", b)
        copy = QPushButton("Copy")
        copy.clicked.connect(self._copy)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self._reload)
        header.addWidget(copy)
        header.addWidget(refresh)
        root.addLayout(header)

        self.view = QPlainTextEdit()
        self.view.setReadOnly(True)
        self.view.setStyleSheet("font-family: 'Cascadia Code','Consolas',monospace; font-size:12px;")
        root.addWidget(self.view, 1)

        self.audit_view = QPlainTextEdit()
        self.audit_view.setReadOnly(True)
        self.audit_view.setMaximumHeight(150)
        self.audit_view.setStyleSheet("font-family: 'Cascadia Code','Consolas',monospace; font-size:12px;")
        root.addWidget(QLabel("Audit trail (who did what)"))
        root.addWidget(self.audit_view)

        self._reload()

    # ── data ──────────────────────────────────────────────────────────────────
    def _set_filter(self, name: str):
        self._filter = name
        for n in ("all", "warn", "error"):
            getattr(self, f"_btn_{n}").setChecked(n == name)
        self._reload()

    def _reload(self):
        lines = _tail(get_log_file_path())
        if self._filter == "warn":
            lines = [ln for ln in lines if "WARNING" in ln or "ERROR" in ln]
        elif self._filter == "error":
            lines = [ln for ln in lines if "ERROR" in ln or "CRITICAL" in ln]
        self.view.setPlainText("".join(lines).rstrip())
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().maximum())
        self._load_audit()

    def _load_audit(self):
        out = []
        for ln in _tail(audit_log_path(), limit=100):
            try:
                e = json.loads(ln)
                det = " ".join(f"{k}={v}" for k, v in (e.get("details") or {}).items())
                tgt = f" [{e['target']}]" if e.get("target") else ""
                out.append(f"{e.get('ts','')}  {e.get('action','')}{tgt}  {det}".rstrip())
            except (ValueError, KeyError):
                continue
        self.audit_view.setPlainText("\n".join(out))
        self.audit_view.verticalScrollBar().setValue(self.audit_view.verticalScrollBar().maximum())

    def _copy(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.view.toPlainText())
