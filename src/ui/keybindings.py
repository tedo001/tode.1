"""
ui/keybindings.py
──────────────────
Centralised keyboard shortcut registration.
"""
import tkinter as tk


class KeyBindings:
    """Register and unregister all application keyboard shortcuts."""

    SHORTCUTS: dict[str, str] = {
        "<Left>":      "prev_frame",
        "<Right>":     "next_frame",
        "<space>":     "next_frame",
        "v":           "view_mode",
        "d":           "draw_mode",
        "<Control-s>": "save",
        "<Control-z>": "undo",
        "<Delete>":    "delete_box",
        "<Escape>":    "deselect",
        "<Control-a>": "annotate_all",
        "<F1>":        "show_shortcuts",
    }

    def __init__(self, root: tk.Tk, handlers: dict) -> None:
        """
        Parameters
        ----------
        root     : tk.Tk — the root window to bind on
        handlers : dict[str, callable] — action_name → callback
        """
        self.root = root
        self.handlers = handlers
        self._bound: list[str] = []

    def bind_all(self) -> None:
        """Register all shortcuts whose handlers are present."""
        for key, action in self.SHORTCUTS.items():
            handler = self.handlers.get(action)
            if handler is not None:
                self.root.bind(key, lambda e, h=handler: h())
                self._bound.append(key)

    def unbind_all(self) -> None:
        """Remove all previously registered shortcuts."""
        for key in self._bound:
            try:
                self.root.unbind(key)
            except tk.TclError:
                pass
        self._bound.clear()

    def rebind(self, handlers: dict) -> None:
        """Update handlers and re-register shortcuts."""
        self.handlers = handlers
        self.unbind_all()
        self.bind_all()
