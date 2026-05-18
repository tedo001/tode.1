"""
ui/dialogs/class_manager.py
────────────────────────────
Modal dialog to manage annotation class names and colours.
"""
import tkinter as tk
from tkinter import simpledialog, ttk

from ui.widgets.color_swatch import ColorSwatch
from utils.config import ACCENT, BG_DARK, BG_PANEL, TEXT_LIGHT

_DEFAULT_COLORS = [
    "#00ff88", "#ff6644", "#44aaff", "#ffdd44", "#cc66ff",
    "#ff44aa", "#44ffcc", "#ffaa44", "#88ff44", "#ff4444",
]


class ClassManagerDialog:
    """
    Manage annotation class names and their associated colours.

    Attributes
    ----------
    result : list[dict] | None
        ``None`` if cancelled; otherwise a list of
        ``{"name": str, "color": str}`` dicts.
    """

    def __init__(
        self,
        master: tk.Misc,
        classes: list[dict] | None = None,
    ) -> None:
        self.result: list[dict] | None = None

        # Internal state: list of {"name": str, "color": str}
        self._classes: list[dict] = list(classes or [{"name": "object", "color": "#00ff88"}])
        self._swatches: dict[int, ColorSwatch] = {}

        self._win = tk.Toplevel(master)
        self._win.title("Class Manager")
        self._win.configure(bg=BG_DARK)
        self._win.resizable(False, False)
        self._win.grab_set()

        self._build()
        self._win.update_idletasks()
        self._center(master)
        master.wait_window(self._win)

    # ── build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        title = tk.Label(
            self._win, text="Class Manager",
            bg=BG_DARK, fg=ACCENT,
            font=("Helvetica", 13, "bold"),
        )
        title.pack(anchor=tk.W, padx=16, pady=(12, 4))

        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # ── Class list ───────────────────────────────────────────────────────
        list_frame = tk.Frame(self._win, bg=BG_PANEL, bd=0)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self._listbox = tk.Listbox(
            list_frame,
            bg=BG_PANEL, fg=TEXT_LIGHT,
            selectbackground=ACCENT, selectforeground=TEXT_LIGHT,
            activestyle="none",
            relief=tk.FLAT, bd=0,
            font=("Helvetica", 10),
            width=28, height=10,
        )
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        # Swatch column
        self._swatch_col = tk.Frame(list_frame, bg=BG_PANEL)
        self._swatch_col.pack(side=tk.LEFT, padx=4, pady=4)

        self._refresh_list()

        # ── Add-new row ──────────────────────────────────────────────────────
        add_row = tk.Frame(self._win, bg=BG_DARK)
        add_row.pack(fill=tk.X, padx=16, pady=4)
        self._new_name = tk.StringVar()
        tk.Entry(
            add_row, textvariable=self._new_name,
            bg=BG_PANEL, fg=TEXT_LIGHT,
            insertbackground=TEXT_LIGHT,
            relief=tk.FLAT, width=22,
        ).pack(side=tk.LEFT)
        tk.Button(
            add_row, text="Add",
            command=self._add_class,
            bg=ACCENT, fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=8, pady=2, bd=0,
        ).pack(side=tk.LEFT, padx=6)

        # ── Action buttons ───────────────────────────────────────────────────
        btn_row = tk.Frame(self._win, bg=BG_DARK)
        btn_row.pack(pady=4)

        for label, cmd in [
            ("Rename", self._rename_class),
            ("Remove", self._remove_class),
        ]:
            tk.Button(
                btn_row, text=label, command=cmd,
                bg="#333355", fg=TEXT_LIGHT,
                relief=tk.FLAT, cursor="hand2",
                padx=10, pady=3, bd=0,
            ).pack(side=tk.LEFT, padx=4)

        # ── OK / Cancel ──────────────────────────────────────────────────────
        ttk.Separator(self._win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=6)
        ok_row = tk.Frame(self._win, bg=BG_DARK)
        ok_row.pack(pady=6)
        tk.Button(
            ok_row, text="Cancel",
            command=self._win.destroy,
            bg="#333355", fg=TEXT_LIGHT,
            relief=tk.FLAT, cursor="hand2",
            padx=12, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            ok_row, text="OK",
            command=self._ok,
            bg=ACCENT, fg=TEXT_LIGHT,
            activebackground="#9d8fff",
            relief=tk.FLAT, cursor="hand2",
            padx=12, pady=4, bd=0,
        ).pack(side=tk.LEFT, padx=6)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, tk.END)
        # Clear old swatches
        for w in self._swatch_col.winfo_children():
            w.destroy()
        self._swatches.clear()

        for i, cls in enumerate(self._classes):
            self._listbox.insert(tk.END, f"  {i}  {cls['name']}")
            color = cls.get("color", _DEFAULT_COLORS[i % len(_DEFAULT_COLORS)])
            sw = ColorSwatch(
                self._swatch_col, color=color, size=18,
                on_change=lambda c, idx=i: self._color_changed(idx, c),
            )
            sw.pack(pady=1, padx=4)
            self._swatches[i] = sw

    # ── actions ───────────────────────────────────────────────────────────────

    def _add_class(self) -> None:
        name = self._new_name.get().strip()
        if not name:
            return
        color = _DEFAULT_COLORS[len(self._classes) % len(_DEFAULT_COLORS)]
        self._classes.append({"name": name, "color": color})
        self._new_name.set("")
        self._refresh_list()

    def _remove_class(self) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._classes):
            self._classes.pop(idx)
            self._refresh_list()

    def _rename_class(self) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        idx  = sel[0]
        old  = self._classes[idx]["name"]
        new  = simpledialog.askstring(
            "Rename class", f"New name for '{old}':",
            parent=self._win, initialvalue=old,
        )
        if new and new.strip():
            self._classes[idx]["name"] = new.strip()
            self._refresh_list()

    def _color_changed(self, idx: int, color: str) -> None:
        if 0 <= idx < len(self._classes):
            self._classes[idx]["color"] = color

    def _ok(self) -> None:
        self.result = list(self._classes)
        self._win.destroy()

    def _center(self, master: tk.Misc) -> None:
        mw = master.winfo_rootx() + master.winfo_width() // 2
        mh = master.winfo_rooty() + master.winfo_height() // 2
        w  = self._win.winfo_width()
        h  = self._win.winfo_height()
        self._win.geometry(f"+{mw - w // 2}+{mh - h // 2}")
