"""
ui/widgets/icon_button.py
──────────────────────────
Button with an emoji icon, hover effect, and optional tooltip.
"""
import tkinter as tk

from ui.widgets.tooltip import Tooltip
from utils.config import ACCENT, BG_PANEL, TEXT_LIGHT


class IconButton(tk.Button):
    """Button with emoji *icon*, label *text*, and hover colour change."""

    _DEFAULT_BG = BG_PANEL
    _HOVER_BG   = ACCENT

    def __init__(
        self,
        master: tk.Misc,
        icon: str,
        text: str,
        command,
        tooltip: str = "",
        **kw,
    ) -> None:
        kw.setdefault("bg",              self._DEFAULT_BG)
        kw.setdefault("fg",              TEXT_LIGHT)
        kw.setdefault("activebackground", self._HOVER_BG)
        kw.setdefault("activeforeground", TEXT_LIGHT)
        kw.setdefault("relief",           tk.FLAT)
        kw.setdefault("cursor",           "hand2")
        kw.setdefault("bd",               0)
        kw.setdefault("padx",             8)
        kw.setdefault("pady",             4)
        kw.setdefault("font",             ("Helvetica", 10))
        display = f"{icon}  {text}" if text else icon
        super().__init__(master, text=display, command=command, **kw)

        self._default_bg = kw["bg"]
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        if tooltip:
            Tooltip(self, tooltip)

    def _on_enter(self, e=None) -> None:  # noqa: ARG002
        self.configure(bg=self._HOVER_BG)

    def _on_leave(self, e=None) -> None:  # noqa: ARG002
        self.configure(bg=self._default_bg)
