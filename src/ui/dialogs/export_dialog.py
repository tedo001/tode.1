"""
ui/dialogs/export_dialog.py
────────────────────────────
Export dialog: choose format (COCO / YOLO / Pascal / CSV), train/val/test split,
what to include, and the destination. Returns the chosen options; the caller
runs the export.
"""
from __future__ import annotations

import os

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

_FORMATS = [
    ("coco", "COCO", "json"),
    ("yolo", "YOLO", "txt"),
    ("pascal_voc", "Pascal", "xml"),
    ("csv", "CSV", "flat"),
]


class ExportDialog(QDialog):
    """Collects export options; read `.options` after exec() returns accepted."""

    def __init__(self, parent, default_dir: str, n_frames: int, n_boxes: int,
                 n_below: int = 0, n_empty: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Export dataset")
        self.setMinimumWidth(500)
        self._dir = default_dir
        self.options: dict | None = None

        root = QVBoxLayout(self)

        # format
        root.addWidget(self._section("FORMAT"))
        fmt_row = QHBoxLayout()
        self._fmt_group = QButtonGroup(self)
        for i, (key, name, ext) in enumerate(_FORMATS):
            b = QPushButton(f"{name}\n{ext}")
            b.setCheckable(True)
            b.setMinimumHeight(52)
            b.setProperty("fmt", key)
            if i == 0:
                b.setChecked(True)
            self._fmt_group.addButton(b, i)
            fmt_row.addWidget(b)
        root.addLayout(fmt_row)

        # split
        head = QHBoxLayout()
        head.addWidget(self._section("SPLIT"))
        head.addStretch(1)
        head.addWidget(QLabel(f"{n_boxes:,} boxes · {n_frames:,} frames"))
        root.addLayout(head)
        split_row = QHBoxLayout()
        self.train = self._pct("train", 70)
        self.val = self._pct("val", 20)
        self.test = self._pct("test", 10)
        for w in (self.train, self.val, self.test):
            split_row.addWidget(w)
        split_row.addStretch(1)
        root.addLayout(split_row)

        # include
        root.addWidget(self._section("INCLUDE"))
        self.copy_images = QCheckBox("Copy image frames alongside labels")
        self.copy_images.setChecked(True)
        self.write_tracks = QCheckBox("Write track IDs as attributes")
        self.write_tracks.setChecked(True)
        self.include_below = QCheckBox(f"Include boxes below confidence threshold  ({n_below})")
        self.include_empty = QCheckBox(f"Include frames with zero boxes as negatives  ({n_empty})")
        for cb in (self.copy_images, self.write_tracks, self.include_below, self.include_empty):
            root.addWidget(cb)

        # destination
        root.addWidget(self._section("DESTINATION"))
        dest_row = QHBoxLayout()
        self.dest_label = QLabel(self._dir)
        self.dest_label.setStyleSheet("color:#8b909c;")
        change = QPushButton("change")
        change.clicked.connect(self._pick_dir)
        dest_row.addWidget(self.dest_label, 1)
        dest_row.addWidget(change)
        root.addLayout(dest_row)

        # buttons
        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        export = QPushButton("Export")
        export.setObjectName("primary")
        export.clicked.connect(self._accept)
        btns.addWidget(cancel)
        btns.addWidget(export)
        root.addLayout(btns)

    # ── helpers ────────────────────────────────────────────────────────────────
    def _section(self, text: str) -> QLabel:
        lab = QLabel(text)
        lab.setStyleSheet("color:#8b909c; font-size:11px; font-weight:600; letter-spacing:1px;")
        return lab

    def _pct(self, name: str, value: int) -> QSpinBox:
        sb = QSpinBox()
        sb.setRange(0, 100)
        sb.setValue(value)
        sb.setSuffix(f"%  {name}")
        return sb

    def _pick_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Export destination", self._dir)
        if d:
            self._dir = d
            self.dest_label.setText(d)

    def _selected_format(self) -> str:
        btn = self._fmt_group.checkedButton()
        return btn.property("fmt") if btn else "coco"

    def _accept(self):
        total = self.train.value() + self.val.value() + self.test.value()
        if total != 100:
            self.dest_label.setText("⚠ split must total 100%  ·  " + self._dir)
            return
        self.options = {
            "format": self._selected_format(),
            "out_dir": self._dir,
            "split": (self.train.value(), self.val.value(), self.test.value()),
            "copy_images": self.copy_images.isChecked(),
            "write_track_ids": self.write_tracks.isChecked(),
            "include_below": self.include_below.isChecked(),
            "include_empty": self.include_empty.isChecked(),
        }
        self.accept()


def default_export_dir(base: str) -> str:
    from datetime import date
    return os.path.join(base, f"export_{date.today().isoformat()}")
