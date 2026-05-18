"""
ui/dialogs/about_dialog.py
───────────────────────────
Modal "About tode" dialog showing version, license, and key dependencies.
"""
import platform
import sys
import tkinter as tk
from tkinter import ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT

_VERSION = "1.0.0"

_LOGO = r"""
  _            _
 | |_ ___   __| | ___
 | __/ _ \ / _` |/ _ \
 | || (_) | (_| |  __/
  \__\___/ \__,_|\___|
"""

_LICENSE = (
    "Licensed under the MIT License.\n"
    "YOLO weights may be subject to AGPL-3.0.\n"
    "See LICENSE file for full details."
)


class AboutDialog:
    """
    Show a modal About dialog.

    Usage::

        AboutDialog(parent)
    """

    def __init__(self, master: tk.Misc) -> None:
        self._win = tk.Toplevel(master)
        self._win.title("About tode")
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build()
        self._win.update_idletasks()
        self._center(master)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        pad = {"padx": 20, "pady": 6}

        # Logo
        logo_lbl = tk.Label(
            self._win, text=_LOGO,
            bg=BG_DARK, fg=ACCENT,
            font=("Courier", 10, "bold"),
            justify=tk.LEFT,
        )
        logo_lbl.pack(**pad)

        # Version row
        ver_frame = tk.Frame(self._win, bg=BG_DARK)
        ver_frame.pack(fill=tk.X, **pad)
        tk.Label(
            ver_frame, text="Version:", bg=BG_DARK, fg="#8888aa",
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT)
        tk.Label(
            ver_frame, text=_VERSION, bg=BG_DARK, fg=TEXT_LIGHT,
            font=("Helvetica", 10, "bold"),
        ).pack(side=tk.LEFT, padx=6)

        # Python version
        py_frame = tk.Frame(self._win, bg=BG_DARK)
        py_frame.pack(fill=tk.X, padx=20, pady=2)
        tk.Label(
            py_frame, text="Python:", bg=BG_DARK, fg="#8888aa",
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT)
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        tk.Label(
            py_frame, text=py_ver, bg=BG_DARK, fg=TEXT_LIGHT,
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT, padx=6)

        # Platform
        plat_frame = tk.Frame(self._win, bg=BG_DARK)
        plat_frame.pack(fill=tk.X, padx=20, pady=2)
        tk.Label(
            plat_frame, text="Platform:", bg=BG_DARK, fg="#8888aa",
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT)
        tk.Label(
            plat_frame, text=platform.system(), bg=BG_DARK, fg=TEXT_LIGHT,
            font=("Helvetica", 10),
        ).pack(side=tk.LEFT, padx=6)

        # Separator
        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=20, pady=8
        )

        # Key dependencies
        deps_lbl = tk.Label(
            self._win, text="Key dependencies:",
            bg=BG_DARK, fg="#8888aa", font=("Helvetica", 9),
        )
        deps_lbl.pack(anchor=tk.W, padx=20)
        for dep in ("tkinter", "opencv-python", "numpy", "ultralytics / onnxruntime"):
            tk.Label(
                self._win, text=f"  • {dep}",
                bg=BG_DARK, fg=TEXT_LIGHT, font=("Helvetica", 9),
                anchor=tk.W,
            ).pack(fill=tk.X, padx=20)

        # Separator
        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=20, pady=8
        )

        # License
        lic_lbl = tk.Label(
            self._win, text=_LICENSE,
            bg=BG_PANEL, fg="#aaaacc",
            font=("Helvetica", 9), justify=tk.LEFT,
            padx=10, pady=6,
        )
        lic_lbl.pack(fill=tk.X, padx=20)

        # Close button
        tk.Button(
            self._win, text="Close",
            command=self._win.destroy,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            activeforeground=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=20, pady=4, bd=0,
        ).pack(pady=14)

    def _center(self, master: tk.Misc) -> None:
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        w  = self._win.winfo_width()
        h  = self._win.winfo_height()
        self._win.geometry(f"+{mw - w // 2}+{mh - h // 2}")
