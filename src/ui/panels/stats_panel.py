"""
ui/panels/stats_panel.py
──────────────────────────
Side panel displaying live annotation statistics.
"""
import tkinter as tk

from utils.config import ACCENT, BG_PANEL, TEXT_LIGHT


class StatsPanel(tk.Frame):
    """
    Embeddable panel showing annotation counts and class distribution.

    Call :meth:`update_stats` to refresh displayed data.
    """

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=BG_PANEL, **kwargs)

        tk.Label(
            self, text="Statistics",
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 10, "bold"),
        ).pack(anchor=tk.W, padx=8, pady=(8, 2))

        self._total_var  = tk.StringVar(value="Total annotations: 0")
        self._frames_var = tk.StringVar(value="Annotated frames: 0")
        self._classes_var = tk.StringVar(value="Classes: 0")

        for var in (self._total_var, self._frames_var, self._classes_var):
            tk.Label(
                self, textvariable=var,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                font=("Helvetica", 9),
                anchor=tk.W,
            ).pack(fill=tk.X, padx=10, pady=1)

        self._dist_frame = tk.Frame(self, bg=BG_PANEL)
        self._dist_frame.pack(fill=tk.X, padx=8, pady=4)

    def update_stats(
        self,
        total: int,
        annotated_frames: int,
        class_dist: dict[str, int],
    ) -> None:
        """Refresh all displayed statistics."""
        self._total_var.set(f"Total annotations: {total}")
        self._frames_var.set(f"Annotated frames: {annotated_frames}")
        self._classes_var.set(f"Classes: {len(class_dist)}")

        for widget in self._dist_frame.winfo_children():
            widget.destroy()

        for cls, count in sorted(class_dist.items(), key=lambda x: -x[1]):
            row = tk.Frame(self._dist_frame, bg=BG_PANEL)
            row.pack(fill=tk.X, pady=1)
            tk.Label(
                row, text=cls, width=12,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                font=("Helvetica", 8), anchor=tk.W,
            ).pack(side=tk.LEFT)
            tk.Label(
                row, text=str(count),
                bg=BG_PANEL, fg=ACCENT,
                font=("Helvetica", 8, "bold"),
            ).pack(side=tk.RIGHT, padx=4)
