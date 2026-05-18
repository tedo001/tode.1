"""
ui/dialogs/filter_dialog.py
──────────────────────────────
Modal dialog to filter visible annotation classes.
"""
import tkinter as tk
from tkinter import ttk

from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT


class FilterDialog:
    """
    Show a checklist of class names; return selected set.

    Attributes
    ----------
    result : set[str] | None
        ``None`` if cancelled; otherwise the set of classes to show.
    """

    def __init__(self, master: tk.Misc, class_names: list[str], active: set[str] | None = None) -> None:
        self.result: set[str] | None = None

        if active is None:
            active = set(class_names)

        self._vars: dict[str, tk.BooleanVar] = {
            name: tk.BooleanVar(value=(name in active))
            for name in class_names
        }

        self._win = tk.Toplevel(master)
        self._win.title("Filter Classes")
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build(class_names)
        self._win.update_idletasks()
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        self._win.geometry(
            f"+{mw - self._win.winfo_width() // 2}+{mh - self._win.winfo_height() // 2}"
        )
        master.wait_window(self._win)

    def _build(self, class_names: list[str]) -> None:
        pad = {"padx": 16, "pady": 6}

        tk.Label(
            self._win, text="Filter Visible Classes",
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 13, "bold"),
        ).pack(anchor=tk.W, **pad)

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # Select all / none buttons
        btn_row = tk.Frame(self._win, bg=BG_DARK)
        btn_row.pack(anchor=tk.W, padx=16, pady=2)
        tk.Button(
            btn_row, text="All",
            command=lambda: self._set_all(True),
            bg=ACCENT, fg=TEXT_LIGHT, relief=tk.FLAT,
            cursor="hand2", padx=8, pady=2, bd=0,
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(
            btn_row, text="None",
            command=lambda: self._set_all(False),
            bg="#444466", fg=TEXT_LIGHT, relief=tk.FLAT,
            cursor="hand2", padx=8, pady=2, bd=0,
        ).pack(side=tk.LEFT, padx=2)

        # Scrollable checklist
        list_frame = tk.Frame(self._win, bg=BG_PANEL)
        list_frame.pack(fill=tk.X, padx=16, pady=4)

        canvas = tk.Canvas(list_frame, bg=BG_PANEL, height=200, bd=0, highlightthickness=0)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=BG_PANEL)
        canvas.create_window((0, 0), window=inner, anchor=tk.NW)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for name, var in self._vars.items():
            tk.Checkbutton(
                inner, text=name, variable=var,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                activebackground=BG_PANEL, selectcolor=BG_DARK,
                font=("Helvetica", 10), anchor=tk.W,
            ).pack(fill=tk.X, padx=6, pady=1)

        # Buttons
        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=8)
        act_row = tk.Frame(self._win, bg=BG_DARK)
        act_row.pack(pady=6)
        tk.Button(
            act_row, text="Cancel",
            command=self._win.destroy,
            bg="#333355", fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            act_row, text="Apply",
            command=self._apply,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)

    def _set_all(self, state: bool) -> None:
        for var in self._vars.values():
            var.set(state)

    def _apply(self) -> None:
        self.result = {name for name, var in self._vars.items() if var.get()}
        self._win.destroy()
