"""
ui/panels/preview_panel.py
────────────────────────────
Small thumbnail preview of the current frame with annotation boxes.
"""
from __future__ import annotations

import tkinter as tk

from utils.config import ACCENT, BG_DARK, BG_PANEL

try:
    from PIL import Image, ImageTk  # type: ignore
    _PIL = True
except ImportError:
    _PIL = False


class PreviewPanel(tk.Frame):
    """Displays a scaled-down thumbnail of the current annotated frame."""

    _W = 180
    _H = 120

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=BG_PANEL, **kwargs)

        tk.Label(
            self, text="Preview",
            bg=BG_PANEL, fg=ACCENT,
            font=("Helvetica", 9, "bold"),
        ).pack(anchor=tk.W, padx=6, pady=(6, 2))

        self._canvas = tk.Canvas(
            self, width=self._W, height=self._H,
            bg=BG_DARK, bd=0, highlightthickness=1,
            highlightbackground=ACCENT,
        )
        self._canvas.pack(padx=6, pady=4)
        self._photo = None

    def set_frame(self, img) -> None:
        """Accept a numpy BGR frame or PIL Image and display it as a thumbnail."""
        if img is None:
            self._canvas.delete("all")
            return

        if not _PIL:
            return

        if not isinstance(img, Image.Image):
            import cv2  # type: ignore
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
        else:
            pil = img

        pil.thumbnail((self._W, self._H), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(pil)
        self._canvas.delete("all")
        self._canvas.create_image(
            self._W // 2, self._H // 2,
            anchor=tk.CENTER, image=self._photo,
        )
