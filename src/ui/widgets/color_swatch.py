"""
ui/widgets/color_swatch.py
───────────────────────────
Small clickable colour square that opens the system colour chooser.
"""
import tkinter as tk
from tkinter import colorchooser


class ColorSwatch(tk.Canvas):
    """Clickable square that shows *color* and lets the user pick a new one."""

    def __init__(
        self,
        master: tk.Misc,
        color: str = "#ff0000",
        size: int = 18,
        on_change=None,
        **kw,
    ) -> None:
        kw.setdefault("highlightthickness", 1)
        kw.setdefault("highlightbackground", "#555577")
        kw.setdefault("cursor", "hand2")
        super().__init__(master, width=size, height=size, **kw)

        self._color     = color
        self._size      = size
        self._on_change = on_change
        self._rect_id   = self.create_rectangle(
            1, 1, size - 1, size - 1, fill=color, outline=""
        )
        self.bind("<Button-1>", self._pick)

    # ── public API ────────────────────────────────────────────────────────────

    def get_color(self) -> str:
        """Return the current hex colour string."""
        return self._color

    def set_color(self, color: str) -> None:
        """Set colour programmatically (no callback fired)."""
        self._color = color
        self.itemconfigure(self._rect_id, fill=color)

    # ── private ───────────────────────────────────────────────────────────────

    def _pick(self, event=None) -> None:  # noqa: ARG002
        result = colorchooser.askcolor(color=self._color, title="Pick colour")
        if result and result[1]:
            self.set_color(result[1])
            if self._on_change:
                self._on_change(result[1])
