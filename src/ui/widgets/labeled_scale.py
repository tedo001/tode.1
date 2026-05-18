"""
ui/widgets/labeled_scale.py
────────────────────────────
Horizontal Scale widget with a live value Label on the right.
"""
import tkinter as tk

from utils.config import ACCENT, BG_PANEL, TEXT_LIGHT


class LabeledScale(tk.Frame):
    """A labelled Scale that shows its current value formatted with *fmt*."""

    def __init__(
        self,
        master: tk.Misc,
        label: str,
        from_: float,
        to: float,
        resolution: float,
        variable: tk.DoubleVar,
        fmt: str = "{:.2f}",
        command=None,
        **kw,
    ) -> None:
        kw.setdefault("bg", BG_PANEL)
        super().__init__(master, **kw)

        self._fmt      = fmt
        self._var      = variable
        self._command  = command

        # Label (left)
        tk.Label(
            self, text=label, bg=BG_PANEL, fg=TEXT_LIGHT,
            font=("Helvetica", 9), width=18, anchor="w",
        ).pack(side=tk.LEFT)

        # Scale (middle)
        self._scale = tk.Scale(
            self,
            from_=from_, to=to,
            resolution=resolution,
            orient=tk.HORIZONTAL,
            variable=variable,
            command=self._on_change,
            bg=BG_PANEL, fg=TEXT_LIGHT,
            troughcolor="#1e1e2e",
            activebackground=ACCENT,
            highlightthickness=0,
            sliderlength=14,
            showvalue=False,
            length=160,
        )
        self._scale.pack(side=tk.LEFT, padx=6)

        # Value display (right)
        self._val_var = tk.StringVar(value=fmt.format(variable.get()))
        tk.Label(
            self, textvariable=self._val_var,
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 9, "bold"), width=6, anchor="e",
        ).pack(side=tk.LEFT)

    def _on_change(self, value) -> None:
        self._val_var.set(self._fmt.format(float(value)))
        if self._command:
            self._command(float(value))
