"""
ui/panels/history_panel.py
────────────────────────────
Side panel showing the undo/redo action history stack.
"""
import tkinter as tk
from collections import deque

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT

_MAX_HISTORY = 50


class HistoryPanel(tk.Frame):
    """Displays the last N actions for reference (read-only)."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=BG_PANEL, **kwargs)
        self._history: deque[str] = deque(maxlen=_MAX_HISTORY)

        tk.Label(
            self, text="History",
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=8, pady=(8, 2))

        frame = tk.Frame(self, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        scroll = tk.Scrollbar(frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            frame,
            yscrollcommand=scroll.set,
            bg=BG_DARK, fg=TEXT_LIGHT,
            selectbackground=ACCENT,
            font=("Consolas", 8),
            relief=tk.FLAT, bd=0,
            activestyle="none",
        )
        self._listbox.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self._listbox.yview)

    def push(self, action: str) -> None:
        """Record a new action string."""
        self._history.append(action)
        self._listbox.insert(tk.END, action)
        if self._listbox.size() > _MAX_HISTORY:
            self._listbox.delete(0)
        self._listbox.see(tk.END)

    def clear(self) -> None:
        self._history.clear()
        self._listbox.delete(0, tk.END)
