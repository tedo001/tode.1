"""
ui/widgets/tooltip.py
──────────────────────
Hover tooltip that appears near any widget.
"""
import tkinter as tk

from utils.config import BG_PANEL, TEXT_LIGHT


class Tooltip:
    """Show a dark tooltip popup on hover over *widget*."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text   = text
        self._tip:  tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None) -> None:  # noqa: ARG002
        if self._tip or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4

        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            self._tip,
            text=self.text,
            bg=BG_PANEL,
            fg=TEXT_LIGHT,
            relief=tk.SOLID,
            bd=1,
            padx=6,
            pady=3,
            font=("Helvetica", 9),
        )
        lbl.pack()

    def _hide(self, event=None) -> None:  # noqa: ARG002
        if self._tip:
            self._tip.destroy()
            self._tip = None
