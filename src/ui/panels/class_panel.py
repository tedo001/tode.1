"""
ui/panels/class_panel.py
──────────────────────────
Side panel listing annotation classes with per-class visibility toggles.
"""
import tkinter as tk
from tkinter import ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class ClassPanel(tk.Frame):
    """
    Panel listing classes with eye-toggle buttons for visibility control.

    Pass *on_visibility_change* callback to receive ``(class_name, bool)`` events.
    """

    def __init__(self, master: tk.Misc, on_visibility_change=None, **kwargs) -> None:
        super().__init__(master, bg=BG_PANEL, **kwargs)
        self._callback = on_visibility_change
        self._visibility: dict[str, tk.BooleanVar] = {}

        tk.Label(
            self, text="Classes",
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=8, pady=(8, 2))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=6, pady=2)

        self._list_frame = tk.Frame(self, bg=BG_PANEL)
        self._list_frame.pack(fill=tk.BOTH, expand=True, padx=4)

    def set_classes(self, class_names: list[str]) -> None:
        """Rebuild the class list widget."""
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._visibility.clear()

        for name in class_names:
            var = tk.BooleanVar(value=True)
            self._visibility[name] = var
            row = tk.Frame(self._list_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=1)
            tk.Label(
                row, text=name,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                font=("Helvetica", 9), anchor=tk.W,
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Checkbutton(
                row, variable=var,
                command=lambda n=name, v=var: self._toggle(n, v),
                bg=BG_PANEL, activebackground=BG_PANEL,
                selectcolor=BG_DARK,
            ).pack(side=tk.RIGHT)

    def _toggle(self, name: str, var: tk.BooleanVar) -> None:
        if self._callback:
            self._callback(name, var.get())

    def get_visible(self) -> set[str]:
        """Return set of class names currently visible."""
        return {n for n, v in self._visibility.items() if v.get()}
