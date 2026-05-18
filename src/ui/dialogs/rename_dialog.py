"""
ui/dialogs/rename_dialog.py
─────────────────────────────
Simple single-field rename / input dialog.
"""
import tkinter as tk
from tkinter import ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class RenameDialog:
    """
    Ask the user for a new name.

    Attributes
    ----------
    result : str | None
        ``None`` if cancelled; otherwise the entered name (stripped).
    """

    def __init__(self, master: tk.Misc, title: str = "Rename", current: str = "") -> None:
        self.result: str | None = None

        self._var = tk.StringVar(value=current)

        self._win = tk.Toplevel(master)
        self._win.title(title)
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build(title)
        self._win.update_idletasks()
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        self._win.geometry(
            f"+{mw - self._win.winfo_width() // 2}+{mh - self._win.winfo_height() // 2}"
        )
        master.wait_window(self._win)

    def _build(self, title: str) -> None:
        pad = {"padx": 20, "pady": 8}

        tk.Label(
            self._win, text=title,
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 12, "bold"),
        ).pack(anchor=tk.W, **pad)

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=4)

        inner = tk.Frame(self._win, bg=BG_PANEL)
        inner.pack(fill=tk.X, padx=20, pady=4)
        tk.Label(
            inner, text="Name:", bg=BG_PANEL, fg=TEXT_LIGHT,
            font=("Helvetica", 10),
        ).pack(anchor=tk.W, padx=6, pady=4)
        entry = tk.Entry(
            inner, textvariable=self._var,
            bg=BG_DARK, fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            relief=tk.FLAT, width=30,
            font=("Helvetica", 10),
        )
        entry.pack(fill=tk.X, padx=6, pady=(0, 6), ipady=4)
        entry.focus_set()
        entry.select_range(0, tk.END)
        entry.bind("<Return>", lambda _: self._confirm())

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=6)

        btn_row = tk.Frame(self._win, bg=BG_DARK)
        btn_row.pack(pady=8)
        tk.Button(
            btn_row, text="Cancel",
            command=self._win.destroy,
            bg="#333355", fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            btn_row, text="OK",
            command=self._confirm,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)

    def _confirm(self) -> None:
        name = self._var.get().strip()
        if name:
            self.result = name
        self._win.destroy()
