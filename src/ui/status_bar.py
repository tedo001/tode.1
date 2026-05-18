"""
ui/status_bar.py
─────────────────
Bottom status bar showing frame info, model name, mode, and box count.
"""
import tkinter as tk

from utils.config import ACCENT, BG_PANEL, TEXT_LIGHT


class StatusBar(tk.Frame):
    """Persistent bottom bar with labelled status fields."""

    _FIELD_BG  = BG_PANEL
    _FIELD_FG  = TEXT_LIGHT
    _SEP_COLOR = "#3a3a5e"

    def __init__(self, master: tk.Misc, **kw) -> None:
        kw.setdefault("bg", self._FIELD_BG)
        kw.setdefault("height", 24)
        super().__init__(master, **kw)
        self.pack_propagate(False)

        self._msg_after: str | None = None
        self._fields: dict[str, tk.StringVar] = {}

        # Build all status segments left → right
        self._lbl_frame    = self._add_field("frame",     "Frame: --/--",  width=14)
        self._sep()
        self._lbl_annotated = self._add_field("annotated", "Ann: 0/0",     width=10)
        self._sep()
        self._lbl_boxes    = self._add_field("boxes",     "Boxes: 0",      width=9)
        self._sep()
        self._lbl_mode     = self._add_field("mode",      "VIEW",          width=7,
                                             fg=ACCENT)
        self._sep()
        self._lbl_model    = self._add_field("model",     "No model",      width=20)

        # Temporary message area (right side)
        self._msg_var = tk.StringVar(value="")
        self._msg_lbl = tk.Label(
            self, textvariable=self._msg_var,
            bg=self._FIELD_BG, fg="#aaaacc",
            font=("Helvetica", 9, "italic"),
            anchor="e",
        )
        self._msg_lbl.pack(side=tk.RIGHT, padx=6)

    # ── public API ────────────────────────────────────────────────────────────

    def set_frame(self, idx: int, total: int) -> None:
        self._fields["frame"].set(f"Frame: {idx + 1}/{total}")

    def set_model(self, name: str) -> None:
        short = name if len(name) <= 20 else "…" + name[-18:]
        self._fields["model"].set(short)

    def set_mode(self, mode: str) -> None:
        self._fields["mode"].set(mode.upper())

    def set_boxes(self, count: int) -> None:
        self._fields["boxes"].set(f"Boxes: {count}")

    def set_annotated(self, count: int, total: int) -> None:
        self._fields["annotated"].set(f"Ann: {count}/{total}")

    def set_message(self, msg: str, duration_ms: int = 3000) -> None:
        """Show a temporary message that auto-clears after *duration_ms* ms."""
        if self._msg_after is not None:
            try:
                self.after_cancel(self._msg_after)
            except tk.TclError:
                pass
        self._msg_var.set(msg)
        self._msg_after = self.after(duration_ms, self._clear_message)

    # ── private ───────────────────────────────────────────────────────────────

    def _clear_message(self) -> None:
        self._msg_var.set("")
        self._msg_after = None

    def _add_field(
        self,
        key: str,
        default: str,
        width: int = 12,
        fg: str = _FIELD_FG,
    ) -> tk.Label:
        var = tk.StringVar(value=default)
        self._fields[key] = var
        lbl = tk.Label(
            self, textvariable=var,
            bg=self._FIELD_BG, fg=fg,
            font=("Helvetica", 9),
            width=width,
            anchor="w",
        )
        lbl.pack(side=tk.LEFT, padx=4, pady=2)
        return lbl

    def _sep(self) -> None:
        sep = tk.Frame(self, bg=self._SEP_COLOR, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, pady=2)
