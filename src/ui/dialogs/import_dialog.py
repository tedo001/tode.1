"""
ui/dialogs/import_dialog.py
─────────────────────────────
Modal dialog for importing annotations from an external dataset.
"""
import tkinter as tk
from tkinter import filedialog, ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class ImportDialog:
    """
    Modal import dialog.

    Attributes
    ----------
    result : dict | None
        ``None`` if cancelled; otherwise ``{"path": str, "format": str}``.
    """

    _FORMATS = ("YOLO", "COCO JSON", "Pascal VOC", "CSV")

    def __init__(self, master: tk.Misc) -> None:
        self.result: dict | None = None

        self._path_var   = tk.StringVar()
        self._format_var = tk.StringVar(value=self._FORMATS[0])

        self._win = tk.Toplevel(master)
        self._win.title("Import Annotations")
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build()
        self._win.update_idletasks()
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        self._win.geometry(
            f"+{mw - self._win.winfo_width() // 2}+{mh - self._win.winfo_height() // 2}"
        )
        master.wait_window(self._win)

    def _build(self) -> None:
        pad = {"padx": 16, "pady": 6}

        tk.Label(
            self._win, text="Import Annotations",
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 13, "bold"),
        ).pack(anchor=tk.W, **pad)

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # Format selection
        fmt_frame = tk.Frame(self._win, bg=BG_PANEL)
        fmt_frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(
            fmt_frame, text="Format:", bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=4, pady=4)
        for fmt in self._FORMATS:
            tk.Radiobutton(
                fmt_frame, text=fmt,
                variable=self._format_var, value=fmt,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                activebackground=BG_PANEL,
                selectcolor=BG_DARK,
                font=("Helvetica", 10),
            ).pack(anchor=tk.W, padx=12)

        # Path row
        path_frame = tk.Frame(self._win, bg=BG_PANEL)
        path_frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(
            path_frame, text="Source:", bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=4, pady=4)
        row = tk.Frame(path_frame, bg=BG_PANEL)
        row.pack(fill=tk.X, padx=4, pady=2)
        tk.Entry(
            row, textvariable=self._path_var,
            bg=BG_DARK, fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            relief=tk.FLAT, width=32,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            row, text="Browse",
            command=self._browse,
            bg=ACCENT, fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=6, pady=2, bd=0,
        ).pack(side=tk.LEFT, padx=4)

        # Buttons
        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=8)
        btn_row = tk.Frame(self._win, bg=BG_DARK)
        btn_row.pack(pady=6)
        tk.Button(
            btn_row, text="Cancel",
            command=self._win.destroy,
            bg="#333355", fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            btn_row, text="Import",
            command=self._confirm,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)

    def _browse(self) -> None:
        path = filedialog.askdirectory(title="Select annotation directory")
        if path:
            self._path_var.set(path)

    def _confirm(self) -> None:
        path = self._path_var.get().strip()
        if path:
            self.result = {"path": path, "format": self._format_var.get()}
        self._win.destroy()
