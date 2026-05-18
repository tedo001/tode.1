"""
ui/widgets/scrollable_frame.py
───────────────────────────────
Frame with a vertical scrollbar. Add children to `.inner`.
"""
import tkinter as tk

from utils.config import BG_DARK


class ScrollableFrame(tk.Frame):
    """A tk.Frame that wraps a Canvas + Scrollbar to enable vertical scrolling."""

    def __init__(self, master: tk.Misc, **kw) -> None:
        kw.setdefault("bg", BG_DARK)
        super().__init__(master, **kw)

        self._canvas = tk.Canvas(
            self, bg=BG_DARK, highlightthickness=0, bd=0
        )
        self._scrollbar = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._inner = tk.Frame(self._canvas, bg=BG_DARK)
        self._window_id = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse-wheel scrolling
        self._canvas.bind("<MouseWheel>",      self._on_mousewheel)
        self._canvas.bind("<Button-4>",        self._on_scroll_up)
        self._canvas.bind("<Button-5>",        self._on_scroll_down)

    @property
    def inner(self) -> tk.Frame:
        """Add child widgets to this frame."""
        return self._inner

    # ── private ───────────────────────────────────────────────────────────────

    def _on_inner_configure(self, event=None) -> None:  # noqa: ARG002
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._window_id, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_scroll_up(self, event=None) -> None:  # noqa: ARG002
        self._canvas.yview_scroll(-1, "units")

    def _on_scroll_down(self, event=None) -> None:  # noqa: ARG002
        self._canvas.yview_scroll(1, "units")
