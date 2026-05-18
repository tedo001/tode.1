"""
ui/panels/timeline_panel.py
─────────────────────────────
Horizontal timeline widget showing annotation status per frame.
"""
import tkinter as tk

from utils.config import ACCENT, BG_DARK, BG_PANEL


class TimelinePanel(tk.Frame):
    """
    Compact horizontal strip showing annotated vs unannotated frames.

    Click a segment to jump to that frame (calls *on_seek* callback).
    """

    _CELL_W = 4
    _CELL_H = 18

    def __init__(self, master: tk.Misc, on_seek=None, **kwargs) -> None:
        super().__init__(master, bg=BG_PANEL, **kwargs)

        self._on_seek = on_seek
        self._total   = 0
        self._annotated: set[int] = set()
        self._current = 0

        tk.Label(
            self, text="Timeline",
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 9, "bold"),
        ).pack(anchor=tk.W, padx=6, pady=(4, 0))

        self._canvas = tk.Canvas(
            self, height=self._CELL_H + 6,
            bg=BG_DARK, bd=0, highlightthickness=0,
        )
        self._canvas.pack(fill=tk.X, padx=4, pady=4)
        self._canvas.bind("<Configure>", lambda _: self._redraw())
        self._canvas.bind("<Button-1>", self._on_click)

    def set_state(self, total: int, annotated: set[int], current: int) -> None:
        """Update the timeline to reflect new frame state."""
        self._total     = total
        self._annotated = annotated
        self._current   = current
        self._redraw()

    def _redraw(self) -> None:
        self._canvas.delete("all")
        if not self._total:
            return
        w = self._canvas.winfo_width()
        if w < 2:
            return
        cell = max(1, w // self._total)
        for i in range(self._total):
            x0 = i * cell
            x1 = x0 + cell - 1
            if i == self._current:
                color = ACCENT
            elif i in self._annotated:
                color = "#33aa55"
            else:
                color = "#333355"
            self._canvas.create_rectangle(x0, 2, x1, self._CELL_H + 2, fill=color, outline="")

    def _on_click(self, event: tk.Event) -> None:
        if not self._total or not self._on_seek:
            return
        w = self._canvas.winfo_width()
        cell = max(1, w // self._total)
        frame = min(event.x // cell, self._total - 1)
        self._on_seek(frame)
