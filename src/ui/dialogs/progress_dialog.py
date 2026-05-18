"""
ui/dialogs/progress_dialog.py
──────────────────────────────
Non-blocking progress window with a ttk.Progressbar and Cancel button.
"""
import tkinter as tk
from tkinter import ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class ProgressDialog:
    """
    Non-blocking progress window.

    Usage::

        dlg = ProgressDialog(root, title="Processing…", total=100)
        for i in range(100):
            dlg.update(i + 1, f"Step {i + 1}")
            if dlg.cancelled:
                break
        dlg.close()
    """

    def __init__(self, master: tk.Misc, title: str, total: int) -> None:
        self._total      = max(1, total)
        self._cancelled  = False

        self._win = tk.Toplevel(master)
        self._win.title(title)
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._build(title)
        self._win.update_idletasks()
        self._center(master)
        self._win.update()

    # ── public API ────────────────────────────────────────────────────────────

    @property
    def cancelled(self) -> bool:
        """``True`` if the user pressed Cancel."""
        return self._cancelled

    def update(self, current: int, message: str = "") -> None:
        """Advance the progress bar to *current* (1-based)."""
        if not self._win.winfo_exists():
            return
        pct = min(100, int(current / self._total * 100))
        self._bar["value"] = pct
        self._count_var.set(f"{current} / {self._total}")
        if message:
            self._msg_var.set(message)
        self._win.update_idletasks()
        self._win.update()

    def close(self) -> None:
        """Destroy the dialog window."""
        if self._win.winfo_exists():
            self._win.destroy()

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self, title: str) -> None:
        tk.Label(
            self._win, text=title,
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 11, "bold"),
        ).pack(padx=20, pady=(12, 4))

        self._msg_var = tk.StringVar(value="Starting…")
        tk.Label(
            self._win, textvariable=self._msg_var,
            bg=BG_DARK, fg=TEXT_LIGHT,
            font=("Helvetica", 9),
        ).pack(padx=20, pady=2)

        style = ttk.Style(self._win)
        style.configure(
            "Tode.Horizontal.TProgressbar",
            troughcolor=BG_PANEL,
            background=ACCENT,
            borderwidth=0,
        )
        self._bar = ttk.Progressbar(
            self._win, orient=tk.HORIZONTAL,
            length=280, mode="determinate",
            style="Tode.Horizontal.TProgressbar",
        )
        self._bar.pack(padx=20, pady=8)

        self._count_var = tk.StringVar(value=f"0 / {self._total}")
        tk.Label(
            self._win, textvariable=self._count_var,
            bg=BG_DARK, fg="#8888aa",
            font=("Helvetica", 9),
        ).pack()

        tk.Button(
            self._win, text="Cancel",
            command=self._on_cancel,
            bg="#7a3333", fg=TEXT_LIGHT,
            activebackground="#9a4343",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(pady=10)

    def _on_cancel(self) -> None:
        self._cancelled = True

    def _center(self, master: tk.Misc) -> None:
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        w  = self._win.winfo_width()
        h  = self._win.winfo_height()
        self._win.geometry(f"+{mw - w // 2}+{mh - h // 2}")
