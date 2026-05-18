"""
ui/panels/sidebar.py
──────────────────────
Collapsible sidebar container that hosts stats, class list, and history panels.
"""
import tkinter as tk

from ui.panels.class_panel import ClassPanel
from ui.panels.history_panel import HistoryPanel
from ui.panels.stats_panel import StatsPanel
from utils.config import ACCENT, BG_DARK, BG_PANEL


class Sidebar(tk.Frame):
    """
    Right-hand sidebar with collapsible sub-panels.

    Provides :attr:`stats`, :attr:`classes`, and :attr:`history` sub-panels.
    """

    _WIDTH = 200

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=BG_PANEL, width=self._WIDTH, **kwargs)
        self.pack_propagate(False)
        self._collapsed = False

        self._toggle_btn = tk.Button(
            self, text="◀",
            command=self._toggle,
            bg=BG_DARK, fg=ACCENT,
            relief=tk.FLAT, cursor="hand2",
            font=("Helvetica", 10, "bold"),
            bd=0,
        )
        self._toggle_btn.pack(side=tk.TOP, anchor=tk.NE, padx=4, pady=4)

        self._content = tk.Frame(self, bg=BG_PANEL)
        self._content.pack(fill=tk.BOTH, expand=True)

        self.stats   = StatsPanel(self._content)
        self.stats.pack(fill=tk.X)

        tk.Frame(self._content, bg=ACCENT, height=1).pack(fill=tk.X, padx=4, pady=4)

        self.classes = ClassPanel(self._content)
        self.classes.pack(fill=tk.X)

        tk.Frame(self._content, bg=ACCENT, height=1).pack(fill=tk.X, padx=4, pady=4)

        self.history = HistoryPanel(self._content)
        self.history.pack(fill=tk.BOTH, expand=True)

    def _toggle(self) -> None:
        if self._collapsed:
            self.config(width=self._WIDTH)
            self._content.pack(fill=tk.BOTH, expand=True)
            self._toggle_btn.config(text="◀")
        else:
            self._content.pack_forget()
            self.config(width=20)
            self._toggle_btn.config(text="▶")
        self._collapsed = not self._collapsed
