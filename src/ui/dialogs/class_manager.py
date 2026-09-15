"""
ui/dialogs/class_manager.py
────────────────────────────
Class manager: colours, number-key hotkeys, box counts, and rename / merge /
delete-with-boxes over the live annotations.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ui.qt_canvas import _class_color


class ClassManagerDialog(QDialog):
    """Edit the project's class set (name → id) and re-map existing boxes."""

    def __init__(self, parent, manager, class_ids: dict[str, int]):
        super().__init__(parent)
        self.setWindowTitle("Classes")
        self.resize(460, 420)
        self.manager = manager
        self.class_ids = class_ids       # name -> id (mutated in place)

        root = QVBoxLayout(self)
        head = QHBoxLayout()
        head.addWidget(QLabel("<b>Classes</b>"))
        head.addStretch(1)
        add = QPushButton("+ New class")
        add.clicked.connect(self._add)
        head.addWidget(add)
        root.addLayout(head)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["", "Name", "Key", "Boxes"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(0, 32)
        self.table.setColumnWidth(2, 48)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table, 1)

        actions = QHBoxLayout()
        for label, slot in (
            ("Rename", self._rename),
            ("Merge into…", self._merge),
            ("Delete + boxes", self._delete),
        ):
            b = QPushButton(label)
            if label.startswith("Delete"):
                b.setObjectName("danger")
            b.clicked.connect(slot)
            actions.addWidget(b)
        root.addLayout(actions)

        self._reload()

    # ── helpers ────────────────────────────────────────────────────────────────
    def _box_counts(self) -> dict[int, int]:
        counts: dict[int, int] = {}
        if self.manager is not None:
            for ann in self.manager._annotations.values():
                for b in ann.boxes:
                    counts[b.class_id] = counts.get(b.class_id, 0) + 1
        return counts

    def _reload(self):
        counts = self._box_counts()
        rows = sorted(self.class_ids.items(), key=lambda kv: kv[1])
        self.table.setRowCount(len(rows))
        for r, (name, cid) in enumerate(rows):
            swatch = QPixmap(16, 16)
            swatch.fill(QColor(_class_color(cid)))
            ic = QTableWidgetItem()
            ic.setIcon(QIcon(swatch))
            ic.setData(Qt.ItemDataRole.UserRole, cid)
            self.table.setItem(r, 0, ic)
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(str(r + 1) if r < 9 else "—"))
            self.table.setItem(r, 3, QTableWidgetItem(str(counts.get(cid, 0))))

    def _selected(self) -> tuple[str, int] | None:
        r = self.table.currentRow()
        if r < 0:
            return None
        name = self.table.item(r, 1).text()
        return name, self.class_ids.get(name, -1)

    def _apply_to_boxes(self, fn):
        if self.manager is None:
            return
        for ann in self.manager._annotations.values():
            fn(ann)
            ann._refresh_annotated()

    # ── actions ────────────────────────────────────────────────────────────────
    def _add(self):
        name, ok = QInputDialog.getText(self, "New class", "Class name:")
        name = name.strip()
        if ok and name and name not in self.class_ids:
            self.class_ids[name] = max(self.class_ids.values(), default=-1) + 1
            self._reload()

    def _rename(self):
        sel = self._selected()
        if not sel:
            return
        old, cid = sel
        new, ok = QInputDialog.getText(self, "Rename class", "New name:", text=old)
        new = new.strip()
        if ok and new and new != old:
            self.class_ids.pop(old, None)
            self.class_ids[new] = cid

            def _rn(ann):
                for b in ann.boxes:
                    if b.class_id == cid:
                        b.class_name = new
            self._apply_to_boxes(_rn)
            self._reload()

    def _merge(self):
        sel = self._selected()
        if not sel:
            return
        src, src_id = sel
        others = [n for n in self.class_ids if n != src]
        if not others:
            return
        dst, ok = QInputDialog.getItem(self, "Merge", f"Merge '{src}' into:", others, 0, False)
        if not ok:
            return
        dst_id = self.class_ids[dst]

        def _mg(ann):
            for b in ann.boxes:
                if b.class_id == src_id:
                    b.class_id = dst_id
                    b.class_name = dst
        self._apply_to_boxes(_mg)
        self.class_ids.pop(src, None)
        self._reload()

    def _delete(self):
        sel = self._selected()
        if not sel:
            return
        name, cid = sel
        if QMessageBox.question(
            self, "Delete class",
            f"Delete '{name}' and all its boxes?",
        ) != QMessageBox.StandardButton.Yes:
            return

        def _del(ann):
            ann.boxes = [b for b in ann.boxes if b.class_id != cid]
        self._apply_to_boxes(_del)
        self.class_ids.pop(name, None)
        self._reload()
