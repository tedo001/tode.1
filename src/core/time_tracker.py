"""
core/time_tracker.py
─────────────────────
Annotation time tracking. Measures **active** annotation time (idle gaps are
excluded via an auto-pause) plus a per-frame breakdown, so you can answer
"how long did this dataset actually take to annotate?".

Pure logic, no UI — the clock is injectable so it is fully unit-testable. The
UI drives it with:
  • ``tick()``            — called ~1×/sec to accrue elapsed active time
  • ``touch(frame_idx)``  — called on every user action (draw, edit, nav, …)
"""
from __future__ import annotations

import json
import os
import time


class AnnotationTimer:
    """Tracks active annotation time with idle auto-pause + per-frame timing."""

    def __init__(self, idle_timeout: float = 30.0, clock=time.monotonic):
        self._clock = clock
        self._idle_timeout = idle_timeout

        self._active = 0.0                       # accrued active seconds (this session)
        self._frame_seconds: dict[int, float] = {}
        self._current_frame: int | None = None

        self._running = False
        self._last_tick = 0.0
        self._last_activity = 0.0
        self._wall_start = self._clock()

        # Baselines carried over from previous sessions (for cumulative totals).
        self._base_active = 0.0
        self._base_frames: dict[int, float] = {}

    # ── lifecycle ─────────────────────────────────────────────────────────────
    def start(self) -> None:
        now = self._clock()
        self._running = True
        self._last_tick = now
        self._last_activity = now

    def pause(self) -> None:
        """Manually stop accruing (e.g. window lost focus)."""
        self._accrue(self._clock())
        self._running = False

    def resume(self) -> None:
        now = self._clock()
        self._running = True
        self._last_tick = now
        self._last_activity = now

    # ── drivers ───────────────────────────────────────────────────────────────
    def tick(self) -> None:
        """Accrue time since the last tick if the user is not idle."""
        self._accrue(self._clock())

    def touch(self, frame_index: int | None = None) -> None:
        """Record a user action: closes the current interval, marks activity,
        and (optionally) switches the frame the clock attributes time to."""
        now = self._clock()
        self._accrue(now)
        self._last_activity = now
        if not self._running:
            self._running = True
            self._last_tick = now
        if frame_index is not None:
            self._current_frame = frame_index

    def set_frame(self, frame_index: int) -> None:
        """Switch the active frame (accrues remaining time to the old one)."""
        self.touch(frame_index)

    # ── internal ──────────────────────────────────────────────────────────────
    def _accrue(self, now: float) -> None:
        """Add the active portion of [last_tick, now] to the totals.

        Each action grants credit only up to ``idle_timeout`` seconds after it,
        so the interval counts as the overlap of [last_tick, now] with
        [last_activity, last_activity + idle_timeout]. Time past that window
        (the user went idle) is excluded."""
        if self._running:
            active_until = self._last_activity + self._idle_timeout
            start = self._last_tick
            end = min(now, active_until)
            delta = end - start
            if delta > 0:
                self._active += delta
                if self._current_frame is not None:
                    self._frame_seconds[self._current_frame] = (
                        self._frame_seconds.get(self._current_frame, 0.0) + delta
                    )
        self._last_tick = now

    # ── queries ───────────────────────────────────────────────────────────────
    @property
    def active_seconds(self) -> float:
        return self._base_active + self._active

    @property
    def wall_seconds(self) -> float:
        return self._clock() - self._wall_start

    def frame_seconds(self, frame_index: int) -> float:
        return self._base_frames.get(frame_index, 0.0) + self._frame_seconds.get(frame_index, 0.0)

    @property
    def frames_touched(self) -> int:
        return len(set(self._frame_seconds) | set(self._base_frames))

    def summary(self) -> dict:
        n = self.frames_touched
        return {
            "active_seconds": round(self.active_seconds, 1),
            "wall_seconds": round(self.wall_seconds, 1),
            "frames_touched": n,
            "avg_seconds_per_frame": round(self.active_seconds / n, 2) if n else 0.0,
        }

    @staticmethod
    def format_hms(seconds: float) -> str:
        s = int(seconds)
        h, rem = divmod(s, 3600)
        m, s = divmod(rem, 60)
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

    # ── persistence (cumulative across sessions) ────────────────────────────────
    def seed(self, active: float, frame_seconds: dict[int, float] | None = None) -> None:
        """Carry over totals from a previous session as a baseline."""
        self._base_active = max(0.0, float(active))
        self._base_frames = {int(k): float(v) for k, v in (frame_seconds or {}).items()}

    def load(self, path: str) -> None:
        """Seed from a timing.json written by a previous session (if present)."""
        if not os.path.isfile(path):
            return
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.seed(data.get("active_seconds", 0.0), data.get("frame_seconds", {}))
        except (OSError, ValueError):
            pass

    def save(self, path: str) -> None:
        """Persist cumulative timing to timing.json."""
        self._accrue(self._clock())
        frames = dict(self._base_frames)
        for k, v in self._frame_seconds.items():
            frames[k] = frames.get(k, 0.0) + v
        payload = {
            "active_seconds": round(self.active_seconds, 2),
            "frame_seconds": {str(k): round(v, 2) for k, v in frames.items()},
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
