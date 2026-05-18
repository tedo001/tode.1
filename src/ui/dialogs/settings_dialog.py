"""
ui/dialogs/settings_dialog.py
───────────────────────────────
Modal settings dialog. Access result via `.result` after the dialog closes.
"""
import tkinter as tk
from tkinter import filedialog, ttk

from ui.widgets.labeled_scale import LabeledScale
from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class SettingsDialog:
    """
    Modal dialog to configure application settings.

    Attributes
    ----------
    result : dict | None
        ``None`` if the dialog was cancelled; otherwise a dict with keys:
        ``confidence``, ``iou``, ``label_format``, ``model_path``,
        ``auto_save``.
    """

    def __init__(
        self,
        master: tk.Misc,
        *,
        confidence: float = 0.45,
        iou: float = 0.45,
        label_format: str = "yolo",
        model_path: str = "",
        auto_save: bool = False,
    ) -> None:
        self.result: dict | None = None

        self._conf_var   = tk.DoubleVar(value=confidence)
        self._iou_var    = tk.DoubleVar(value=iou)
        self._fmt_var    = tk.StringVar(value=label_format)
        self._model_var  = tk.StringVar(value=model_path)
        self._save_var   = tk.BooleanVar(value=auto_save)

        self._win = tk.Toplevel(master)
        self._win.title("Settings")
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build()
        self._win.update_idletasks()
        self._center(master)
        master.wait_window(self._win)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        pad = {"padx": 16, "pady": 6}

        title = tk.Label(
            self._win, text="Settings",
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 13, "bold"),
        )
        title.pack(anchor=tk.W, **pad)

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # ── Inference thresholds ─────────────────────────────────────────────
        sect = self._section("Inference")
        LabeledScale(
            sect, label="Confidence threshold",
            from_=0.0, to=1.0, resolution=0.01,
            variable=self._conf_var, fmt="{:.2f}",
        ).pack(anchor=tk.W, padx=4, pady=2)
        LabeledScale(
            sect, label="IoU threshold",
            from_=0.0, to=1.0, resolution=0.01,
            variable=self._iou_var, fmt="{:.2f}",
        ).pack(anchor=tk.W, padx=4, pady=2)

        # ── Label format ─────────────────────────────────────────────────────
        fmt_sect = self._section("Label format")
        for fmt in ("yolo", "json"):
            tk.Radiobutton(
                fmt_sect, text=fmt.upper(),
                variable=self._fmt_var, value=fmt,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                activebackground=BG_PANEL,
                selectcolor=BG_DARK,
                font=("Helvetica", 10),
            ).pack(anchor=tk.W, padx=4)

        # ── Model path ───────────────────────────────────────────────────────
        mdl_sect = self._section("Default model path")
        row = tk.Frame(mdl_sect, bg=BG_PANEL)
        row.pack(fill=tk.X, padx=4, pady=2)
        tk.Entry(
            row, textvariable=self._model_var,
            bg=BG_DARK, fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            relief=tk.FLAT, width=30,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(
            row, text="Browse",
            command=self._browse,
            bg=ACCENT, fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=6, pady=2, bd=0,
        ).pack(side=tk.LEFT, padx=4)

        # ── Auto-save toggle ─────────────────────────────────────────────────
        chk_sect = self._section("Behaviour")
        tk.Checkbutton(
            chk_sect, text="Auto-save annotations on frame change",
            variable=self._save_var,
            bg=BG_PANEL, fg=TEXT_LIGHT,
            activebackground=BG_PANEL,
            selectcolor=BG_DARK,
            font=("Helvetica", 10),
        ).pack(anchor=tk.W, padx=4)

        # ── Buttons ──────────────────────────────────────────────────────────
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
            btn_row, text="Apply",
            command=self._apply,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)

    def _section(self, title: str) -> tk.Frame:
        frame = tk.Frame(self._win, bg=BG_PANEL, bd=0)
        frame.pack(fill=tk.X, padx=16, pady=4)
        tk.Label(
            frame, text=title,
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=4, pady=4)
        return frame

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            title="Select model file",
            filetypes=[("Model files", "*.pt *.onnx"), ("All files", "*")],
        )
        if path:
            self._model_var.set(path)

    def _apply(self) -> None:
        self.result = {
            "confidence":   self._conf_var.get(),
            "iou":          self._iou_var.get(),
            "label_format": self._fmt_var.get(),
            "model_path":   self._model_var.get(),
            "auto_save":    self._save_var.get(),
        }
        self._win.destroy()

    def _center(self, master: tk.Misc) -> None:
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        w  = self._win.winfo_width()
        h  = self._win.winfo_height()
        self._win.geometry(f"+{mw - w // 2}+{mh - h // 2}")
