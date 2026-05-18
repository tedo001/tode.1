"""
ui/widgets/confidence_badge.py
───────────────────────────────
Label that shows confidence as coloured text:
  green  (≥ 0.70) — high confidence
  yellow (0.40–0.69) — medium confidence
  red    (< 0.40) — low confidence
"""
import tkinter as tk

from utils.config import BG_PANEL


class ConfidenceBadge(tk.Label):
    """Display a confidence value with traffic-light colour coding."""

    _HIGH_COLOR   = "#00cc66"
    _MEDIUM_COLOR = "#ccaa00"
    _LOW_COLOR    = "#cc3333"

    def __init__(self, master: tk.Misc, **kw) -> None:
        kw.setdefault("bg", BG_PANEL)
        kw.setdefault("font", ("Helvetica", 9, "bold"))
        kw.setdefault("width", 6)
        kw.setdefault("anchor", "center")
        super().__init__(master, text="--", **kw)

    def set_confidence(self, value: float) -> None:
        """Update the displayed value and its colour."""
        pct = max(0.0, min(1.0, value))
        if pct >= 0.70:
            color = self._HIGH_COLOR
        elif pct >= 0.40:
            color = self._MEDIUM_COLOR
        else:
            color = self._LOW_COLOR
        self.configure(text=f"{pct:.0%}", fg=color)
