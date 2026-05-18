"""
ui/theme.py
───────────
Centralised theme constants and helper functions for consistent styling.
"""
import tkinter as tk
from tkinter import ttk


class Theme:
    BG_DARK        = "#1e1e2e"
    BG_PANEL       = "#2a2a3e"
    BG_MEDIUM      = "#252535"
    ACCENT         = "#7c6af7"
    ACCENT_HOVER   = "#9d8fff"
    ACCENT_DIM     = "#5a4fbf"
    TEXT_LIGHT     = "#e0e0f0"
    TEXT_DIM       = "#8888aa"
    SUCCESS        = "#2d8a4e"
    WARNING        = "#b8860b"
    DANGER         = "#7a3333"
    BOX_COLOR      = "#00ff88"
    SELECTED_COLOR = "#ffaa00"

    @staticmethod
    def style_button(btn: tk.Button, variant: str = "primary") -> None:
        """Apply consistent button styling based on variant."""
        base = {
            "relief":          tk.FLAT,
            "cursor":          "hand2",
            "activeforeground": Theme.TEXT_LIGHT,
            "bd":              0,
            "padx":            10,
            "pady":            4,
        }
        if variant == "primary":
            base.update({
                "bg":           Theme.ACCENT,
                "fg":           Theme.TEXT_LIGHT,
                "activebackground": Theme.ACCENT_HOVER,
            })
        elif variant == "danger":
            base.update({
                "bg":           Theme.DANGER,
                "fg":           Theme.TEXT_LIGHT,
                "activebackground": "#9a4343",
            })
        elif variant == "secondary":
            base.update({
                "bg":           Theme.BG_MEDIUM,
                "fg":           Theme.TEXT_LIGHT,
                "activebackground": Theme.BG_PANEL,
            })
        else:
            base.update({
                "bg":           Theme.BG_PANEL,
                "fg":           Theme.TEXT_DIM,
                "activebackground": Theme.BG_MEDIUM,
            })
        btn.configure(**base)

    @staticmethod
    def style_label(lbl: tk.Label, variant: str = "normal") -> None:
        """Apply consistent label styling."""
        base = {"bg": Theme.BG_DARK}
        if variant == "normal":
            base["fg"] = Theme.TEXT_LIGHT
        elif variant == "dim":
            base["fg"] = Theme.TEXT_DIM
        elif variant == "accent":
            base["fg"] = Theme.ACCENT
        elif variant == "success":
            base["fg"] = Theme.BOX_COLOR
        elif variant == "warning":
            base["fg"] = Theme.WARNING
        elif variant == "danger":
            base["fg"] = Theme.DANGER
        lbl.configure(**base)

    @staticmethod
    def apply_treeview_style(style: ttk.Style) -> None:
        """Configure ttk.Treeview to match the dark theme."""
        style.configure(
            "Tode.Treeview",
            background=Theme.BG_MEDIUM,
            foreground=Theme.TEXT_LIGHT,
            fieldbackground=Theme.BG_MEDIUM,
            rowheight=22,
            borderwidth=0,
        )
        style.configure(
            "Tode.Treeview.Heading",
            background=Theme.BG_PANEL,
            foreground=Theme.ACCENT,
            relief=tk.FLAT,
        )
        style.map(
            "Tode.Treeview",
            background=[("selected", Theme.ACCENT_DIM)],
            foreground=[("selected", Theme.TEXT_LIGHT)],
        )
