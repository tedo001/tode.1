"""
ui/widgets/badge.py
────────────────────
Pill-shaped label for counts / status text (e.g. "73 boxes").
"""
import tkinter as tk

from utils.config import ACCENT, TEXT_LIGHT


class Badge(tk.Label):
    """Compact coloured label useful for counts and status indicators."""

    def __init__(
        self,
        master: tk.Misc,
        text: str = "0",
        color: str = ACCENT,
        **kw,
    ) -> None:
        kw.setdefault("bg", color)
        kw.setdefault("fg", TEXT_LIGHT)
        kw.setdefault("font", ("Helvetica", 8, "bold"))
        kw.setdefault("padx", 6)
        kw.setdefault("pady", 2)
        kw.setdefault("relief", tk.FLAT)
        kw.setdefault("bd", 0)
        self._color = color
        super().__init__(master, text=text, **kw)

    def set_count(self, n: int) -> None:
        """Update the displayed integer count."""
        self.configure(text=str(n))

    def set_text(self, text: str) -> None:
        """Update the displayed text."""
        self.configure(text=text)
