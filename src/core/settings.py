"""
core/settings.py
─────────────────
Persisted application settings (inference knobs, UI prefs) with named presets.

Stored as JSON under ``config.CONFIG_DIR``:
  settings.json          — the live settings
  presets/<name>.json    — saved inference presets

Pure logic, no UI. The Settings dialog reads/writes through this.
"""
from __future__ import annotations

import json
import os

from utils.config import (
    CONFIG_DIR,
    DETECT_BATCH_SIZE,
    DETECT_CONFIDENCE,
    DETECT_INPUT_SIZE,
    DETECT_IOU,
    DETECT_MAX_BOXES,
    RTDETR_DEFAULT_MODEL,
)
from utils.logger import get_logger

log = get_logger("core.Settings")

DEFAULTS: dict = {
    # inference
    "checkpoint":             RTDETR_DEFAULT_MODEL,
    "device":                 "auto",        # auto | cpu | cuda:0
    "precision":              "fp16",        # fp16 | fp32
    "input_size":             DETECT_INPUT_SIZE,
    "batch_size":             DETECT_BATCH_SIZE,
    "confidence":             DETECT_CONFIDENCE,
    "nms_iou":                DETECT_IOU,
    "max_boxes":              DETECT_MAX_BOXES,
    "class_agnostic_nms":     False,
    "snap_to_edges":          False,
    "test_time_augmentation": False,
    # workflow
    "track_by_default":       False,
    # ui
    "theme":                  "dark",
}


class Settings:
    """Load/save app settings + inference presets as JSON."""

    def __init__(self, path: str | None = None):
        self.path = path or os.path.join(CONFIG_DIR, "settings.json")
        self._presets_dir = os.path.join(os.path.dirname(self.path), "presets")
        self._data: dict = dict(DEFAULTS)
        self.load()

    # ── core get/set ───────────────────────────────────────────────────────────
    def get(self, key: str, default=None):
        return self._data.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value) -> None:
        self._data[key] = value

    def update(self, values: dict) -> None:
        self._data.update(values)

    def as_dict(self) -> dict:
        return dict(self._data)

    def reset(self) -> None:
        self._data = dict(DEFAULTS)

    # ── persistence ────────────────────────────────────────────────────────────
    def load(self) -> None:
        if not os.path.isfile(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as fh:
                stored = json.load(fh)
            # merge onto defaults so new keys get sane values
            self._data = {**DEFAULTS, **stored}
        except (OSError, ValueError) as exc:
            log.warning(f"Could not read settings ({exc}); using defaults")
            self._data = dict(DEFAULTS)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    # ── presets ────────────────────────────────────────────────────────────────
    def _preset_path(self, name: str) -> str:
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in name) or "preset"
        return os.path.join(self._presets_dir, f"{safe}.json")

    def list_presets(self) -> list[str]:
        if not os.path.isdir(self._presets_dir):
            return []
        return sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(self._presets_dir)
            if f.endswith(".json")
        )

    def save_preset(self, name: str) -> None:
        os.makedirs(self._presets_dir, exist_ok=True)
        with open(self._preset_path(name), "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def load_preset(self, name: str) -> None:
        p = self._preset_path(name)
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as fh:
                self._data = {**DEFAULTS, **json.load(fh)}
