"""
ui/dialogs/export_options_dialog.py
──────────────────────────────────────
Modal dialog for advanced export options.
"""
import tkinter as tk
from tkinter import filedialog, ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class ExportOptionsDialog:
    """
    Modal dialog to configure export options.

    Attributes
    ----------
    result : dict | None
        ``None`` if cancelled; otherwise a dict with export settings.
    """

    _FORMATS = ("YOLO TXT", "COCO JSON", "Pascal VOC XML", "CSV")

    def __init__(self, master: tk.Misc) -> None:
        self.result: dict | None = None

        self._fmt_var    = tk.StringVar(value=self._FORMATS[0])
        self._dest_var   = tk.StringVar()
        self._split_var  = tk.BooleanVar(value=True)
        self._ratio_var  = tk.DoubleVar(value=0.8)
        self._copy_var   = tk.BooleanVar(value=False)

        self._win = tk.Toplevel(master)
        self._win.title("Export Options")
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
            self._win, text="Export Options",
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 13, "bold"),
        ).pack(anchor=tk.W, **pad)
        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # Format
        fmt_frame = self._section("Output Format")
        for fmt in self._FORMATS:
            tk.Radiobutton(
                fmt_frame, text=fmt,
                variable=self._fmt_var, value=fmt,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                activebackground=BG_PANEL,
                selectcolor=BG_DARK,
                font=("Helvetica", 10),
            ).pack(anchor=tk.W, padx=12)

        # Destination
        dest_frame = self._section("Destination Folder")
        row = tk.Frame(dest_frame, bg=BG_PANEL)
        row.pack(fill=tk.X, padx=4, pady=2)
        tk.Entry(
            row, textvariable=self._dest_var,
            bg=BG_DARK, fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            relief=tk.FLAT, width=28,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            row, text="Browse",
            command=self._browse,
            bg=ACCENT, fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=6, pady=2, bd=0,
        ).pack(side=tk.LEFT, padx=4)

        # Options
        opt_frame = self._section("Options")
        tk.Checkbutton(
            opt_frame, text="Train / val split",
            variable=self._split_var,
            bg=BG_PANEL, fg=TEXT_LIGHT,
            activebackground=BG_PANEL, selectcolor=BG_DARK,
            font=("Helvetica", 10),
        ).pack(anchor=tk.W, padx=4)
        tk.Checkbutton(
            opt_frame, text="Copy images to export folder",
            variable=self._copy_var,
            bg=BG_PANEL, fg=TEXT_LIGHT,
            activebackground=BG_PANEL, selectcolor=BG_DARK,
            font=("Helvetica", 10),
        ).pack(anchor=tk.W, padx=4)

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
            btn_row, text="Export",
            command=self._confirm,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)

    def _section(self, title: str) -> tk.Frame:
        frame = tk.Frame(self._win, bg=BG_PANEL)
        frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(
            frame, text=title,
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=4, pady=4)
        return frame

    def _browse(self) -> None:
        path = filedialog.askdirectory(title="Select export destination")
        if path:
            self._dest_var.set(path)

    def _confirm(self) -> None:
        self.result = {
            "format":     self._fmt_var.get(),
            "destination": self._dest_var.get().strip(),
            "split":      self._split_var.get(),
            "train_ratio": self._ratio_var.get(),
            "copy_images": self._copy_var.get(),
        }
        self._win.destroy()
