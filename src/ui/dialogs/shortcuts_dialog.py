"""
ui/dialogs/shortcuts_dialog.py
────────────────────────────────
Read-only modal showing keyboard shortcuts in a table.
"""
import tkinter as tk
from tkinter import ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT

_SHORTCUTS = [
    ("Navigate left",    "Left Arrow"),
    ("Navigate right",   "Right Arrow"),
    ("Next frame",       "Space"),
    ("View mode",        "V"),
    ("Draw mode",        "D"),
    ("Save",             "Ctrl + S"),
    ("Undo",             "Ctrl + Z"),
    ("Delete box",       "Delete"),
    ("Clear selection",  "Escape"),
    ("Annotate all",     "Ctrl + A"),
    ("Zoom in",          "Ctrl + ="),
    ("Zoom out",         "Ctrl + -"),
    ("Reset zoom",       "Ctrl + 0"),
    ("Show shortcuts",   "F1"),
]


class ShortcutsDialog:
    """Display a read-only keyboard shortcuts reference table."""

    def __init__(self, master: tk.Misc) -> None:
        self._win = tk.Toplevel(master)
        self._win.title("Keyboard Shortcuts")
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build()
        self._win.update_idletasks()
        self._center(master)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        title = tk.Label(
            self._win, text="Keyboard Shortcuts",
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 13, "bold"),
        )
        title.pack(anchor=tk.W, padx=16, pady=(12, 4))

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # Style for the treeview
        style = ttk.Style(self._win)
        style.configure(
            "Shortcuts.Treeview",
            background=BG_PANEL,
            foreground=TEXT_LIGHT,
            fieldbackground=BG_PANEL,
            rowheight=24,
            borderwidth=0,
        )
        style.configure(
            "Shortcuts.Treeview.Heading",
            background=BG_DARK,
            foreground=ACCENT,
            relief=tk.FLAT,
        )

        frame = tk.Frame(self._win, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        tree = ttk.Treeview(
            frame,
            columns=("action", "key"),
            show="headings",
            selectmode="none",
            style="Shortcuts.Treeview",
            height=len(_SHORTCUTS),
        )
        tree.heading("action", text="Action")
        tree.heading("key",    text="Key / Combo")
        tree.column("action",  width=180, anchor=tk.W)
        tree.column("key",     width=160, anchor=tk.W)

        for action, key in _SHORTCUTS:
            tree.insert("", tk.END, values=(action, key))

        tree.pack(fill=tk.BOTH, expand=True)

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=6)

        tk.Button(
            self._win, text="Close",
            command=self._win.destroy,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=20, pady=4, bd=0,
        ).pack(pady=8)

    def _center(self, master: tk.Misc) -> None:
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        w  = self._win.winfo_width()
        h  = self._win.winfo_height()
        self._win.geometry(f"+{mw - w // 2}+{mh - h // 2}")
