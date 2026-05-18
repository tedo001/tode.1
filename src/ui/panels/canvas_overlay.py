"""
ui/panels/canvas_overlay.py
─────────────────────────────
Helper that draws annotation boxes over a tkinter Canvas.
"""
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

from utils.config import BOX_COLOR


@dataclass
class Box:
    x1: float
    y1: float
    x2: float
    y2: float
    label: str
    color: str = BOX_COLOR


class CanvasOverlay:
    """
    Draws and manages annotation boxes on a given tk.Canvas.

    Parameters
    ----------
    canvas : tk.Canvas
        The canvas to draw on.
    scale : tuple[float, float]
        ``(scale_x, scale_y)`` to convert normalised coords to canvas px.
    """

    def __init__(self, canvas: tk.Canvas, scale: tuple[float, float] = (1.0, 1.0)) -> None:
        self._canvas = canvas
        self._scale  = scale
        self._items: list[int] = []

    def set_scale(self, sx: float, sy: float) -> None:
        self._scale = (sx, sy)

    def draw_boxes(self, boxes: list[Box]) -> None:
        """Clear previous overlay and draw *boxes*."""
        self.clear()
        sx, sy = self._scale
        for box in boxes:
            x1 = box.x1 * sx
            y1 = box.y1 * sy
            x2 = box.x2 * sx
            y2 = box.y2 * sy
            rect = self._canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=box.color, width=2,
            )
            label = self._canvas.create_text(
                x1 + 2, y1 + 2,
                text=box.label, anchor=tk.NW,
                fill=box.color, font=("Helvetica", 8, "bold"),
            )
            self._items.extend([rect, label])

    def clear(self) -> None:
        for item in self._items:
            self._canvas.delete(item)
        self._items.clear()
