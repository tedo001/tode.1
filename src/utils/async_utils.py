"""
utils/async_utils.py
──────────────────────
Thin helpers for running blocking calls on background threads.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any


def run_in_thread(fn: Callable, *args, callback: Callable[[Any], None] | None = None, daemon: bool = True) -> threading.Thread:
    """
    Run *fn(*args)* on a daemon thread.

    If *callback* is provided it is called with the return value on the same thread as *fn*.
    """
    def _target():
        result = fn(*args)
        if callback:
            callback(result)

    t = threading.Thread(target=_target, daemon=daemon)
    t.start()
    return t


def debounce(fn: Callable, delay_ms: int, widget):
    """
    Return a wrapper that postpones *fn* by *delay_ms* milliseconds.

    Uses tkinter's ``after`` scheduler — must be called from the main thread.
    Subsequent calls within the delay window cancel and reschedule.
    """
    _handle: list[str | None] = [None]

    def wrapper(*args, **kwargs):
        if _handle[0] is not None:
            widget.after_cancel(_handle[0])
        _handle[0] = widget.after(delay_ms, lambda: fn(*args, **kwargs))

    return wrapper
