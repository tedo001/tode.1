"""
utils/shortcuts.py
────────────────────
Centralised keyboard shortcut binding helper.
"""
from __future__ import annotations

import tkinter as tk


class ShortcutManager:
    """
    Register and manage global keyboard shortcuts on a tkinter widget.

    Usage::

        mgr = ShortcutManager(root)
        mgr.bind("<Control-s>", save_fn, description="Save annotations")
    """

    def __init__(self, widget: tk.Widget) -> None:
        self._widget   = widget
        self._bindings: dict[str, tuple[str, callable]] = {}

    def bind(self, key: str, fn: callable, description: str = "") -> None:
        """Bind *key* to *fn*, storing *description* for reference."""
        self._widget.bind(key, lambda _: fn())
        self._bindings[key] = (description, fn)

    def unbind(self, key: str) -> None:
        self._widget.unbind(key)
        self._bindings.pop(key, None)

    def descriptions(self) -> list[tuple[str, str]]:
        """Return ``[(key, description), ...]`` for all registered shortcuts."""
        return [(k, v[0]) for k, v in self._bindings.items()]
