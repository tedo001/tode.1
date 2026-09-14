"""
ui/dialogs/dataset_health.py
─────────────────────────────
"When to stop annotating" panel: dataset-level stats computed from the live
annotations — counts, class balance, confidence distribution, review/empty
counts, duplicate detection, edge boxes, and track breaks.
"""
from __future__ import annotations

from statistics import median

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_REVIEW_CUTOFF = 0.5      # auto boxes below this confidence "need review"


def _iou(a, b) -> float:
    ax1, ay1 = a.x_center - a.width / 2, a.y_center - a.height / 2
    ax2, ay2 = a.x_center + a.width / 2, a.y_center + a.height / 2
    bx1, by1 = b.x_center - b.width / 2, b.y_center - b.height / 2
    bx2, by2 = b.x_center + b.width / 2, b.y_center + b.height / 2
    ix1, iy1, ix2, iy2 = max(ax1, bx1), max(ay1, by1), min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    union = a.width * a.height + b.width * b.height - inter
    return inter / union if union > 0 else 0.0


def compute_health(manager) -> dict:
    """Compute dataset-health metrics from a manager's annotations."""
    anns = list(manager._annotations.values()) if manager else []
    total_frames = len(anns)
    boxes = [b for ann in anns for b in ann.boxes]
    n_boxes = len(boxes)
    empty_frames = sum(1 for ann in anns if not ann.boxes)
    need_review = sum(1 for b in boxes if b.confidence < _REVIEW_CUTOFF)

    class_counts: dict[str, int] = {}
    for b in boxes:
        class_counts[b.class_name] = class_counts.get(b.class_name, 0) + 1

    conf_bins = [0] * 10
    for b in boxes:
        conf_bins[min(9, max(0, int(b.confidence * 10)))] += 1

    areas = [b.width * b.height for b in boxes]
    med_area = median(areas) if areas else 0.0

    duplicates = 0
    edge = 0
    eps = 0.002
    for ann in anns:
        bx = ann.boxes
        for b in bx:
            x1, y1 = b.x_center - b.width / 2, b.y_center - b.height / 2
            x2, y2 = b.x_center + b.width / 2, b.y_center + b.height / 2
            if x1 <= eps or y1 <= eps or x2 >= 1 - eps or y2 >= 1 - eps:
                edge += 1
        for i in range(len(bx)):
            for j in range(i + 1, len(bx)):
                if bx[i].class_id == bx[j].class_id and _iou(bx[i], bx[j]) > 0.9:
                    duplicates += 1

    # track breaks: gaps in the frame sequence of each track id
    track_frames: dict[int, list[int]] = {}
    for ann in anns:
        for b in ann.boxes:
            if b.track_id is not None:
                track_frames.setdefault(b.track_id, []).append(ann.frame_index)
    track_breaks = 0
    for idxs in track_frames.values():
        s = sorted(idxs)
        track_breaks += sum(1 for k in range(1, len(s)) if s[k] - s[k - 1] > 1)

    return {
        "boxes": n_boxes,
        "frames": total_frames,
        "boxes_per_frame": (n_boxes / total_frames) if total_frames else 0.0,
        "need_review": need_review,
        "empty_frames": empty_frames,
        "class_counts": class_counts,
        "conf_bins": conf_bins,
        "median_area": med_area,
        "duplicates": duplicates,
        "edge": edge,
        "track_breaks": track_breaks,
    }


def _tile(value: str, label: str, accent: str = "#e6e8ec") -> QWidget:
    w = QFrame()
    w.setStyleSheet("QFrame{background:#1c1f26;border:1px solid #282c34;border-radius:8px;}")
    lay = QVBoxLayout(w)
    v = QLabel(value)
    v.setStyleSheet(f"font-size:24px;font-weight:700;color:{accent};border:none;")
    lab = QLabel(label)
    lab.setStyleSheet("color:#8b909c;border:none;")
    lay.addWidget(v)
    lay.addWidget(lab)
    return w


class DatasetHealthDialog(QDialog):
    """Dataset-health readout with a recompute button."""

    def __init__(self, parent, manager, conf_threshold: float = 0.5):
        super().__init__(parent)
        self.setWindowTitle("Dataset health")
        self.resize(640, 560)
        self.manager = manager
        self._root = QVBoxLayout(self)
        self._render()

    def _clear(self):
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render(self):
        self._clear()
        if self.manager is None:
            self._root.addWidget(QLabel("No project loaded."))
            return
        h = compute_health(self.manager)

        title = QLabel("<b>Dataset health</b>")
        self._root.addWidget(title)

        tiles = QHBoxLayout()
        tiles.addWidget(_tile(f"{h['boxes']:,}", "boxes"))
        tiles.addWidget(_tile(f"{h['boxes_per_frame']:.2f}", "boxes / frame"))
        tiles.addWidget(_tile(f"{h['need_review']}", "need review", "#e6a23c"))
        tiles.addWidget(_tile(f"{h['empty_frames']}", "empty frames"))
        self._root.addLayout(tiles)

        self._root.addWidget(QLabel("<b>Class balance</b>"))
        maxc = max(h["class_counts"].values(), default=1)
        for name, cnt in sorted(h["class_counts"].items(), key=lambda kv: -kv[1]):
            row = QHBoxLayout()
            lab = QLabel(name)
            lab.setMinimumWidth(120)
            bar = QProgressBar()
            bar.setRange(0, maxc)
            bar.setValue(cnt)
            bar.setTextVisible(False)
            bar.setFixedHeight(12)
            row.addWidget(lab)
            row.addWidget(bar, 1)
            row.addWidget(QLabel(str(cnt)))
            self._root.addLayout(row)

        # rarity warning
        if h["class_counts"]:
            lo = min(h["class_counts"].values())
            hi = max(h["class_counts"].values())
            if lo * 10 < hi:
                rarest = min(h["class_counts"], key=h["class_counts"].get)
                warn = QLabel(
                    f"⚠ '{rarest}' is {hi // max(lo,1)}× rarer than the top class — "
                    "expect weak recall unless you collect more."
                )
                warn.setWordWrap(True)
                warn.setStyleSheet("color:#e6a23c; background:#241f16; border-radius:6px; padding:8px;")
                self._root.addWidget(warn)

        self._root.addWidget(QLabel("<b>Confidence distribution</b>"))
        conf_row = QHBoxLayout()
        maxb = max(h["conf_bins"], default=1) or 1
        for i, c in enumerate(h["conf_bins"]):
            col = QVBoxLayout()
            bar = QProgressBar()
            bar.setOrientation(Qt.Orientation.Vertical)
            bar.setRange(0, maxb)
            bar.setValue(c)
            bar.setTextVisible(False)
            bar.setFixedWidth(22)
            col.addWidget(bar, 1)
            col.addWidget(QLabel(f"{i/10:.1f}"))
            conf_row.addLayout(col)
        self._root.addLayout(conf_row)

        grid = QGridLayout()
        stats = [
            ("median box area", f"{h['median_area']*100:.1f}% of frame"),
            ("duplicate / overlapping", str(h["duplicates"])),
            ("boxes touching frame edge", str(h["edge"])),
            ("track breaks", str(h["track_breaks"])),
        ]
        for r, (k, v) in enumerate(stats):
            key = QLabel(k)
            key.setStyleSheet("color:#8b909c;")
            grid.addWidget(key, r, 0)
            grid.addWidget(QLabel(v), r, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self._root.addLayout(grid)

        btns = QHBoxLayout()
        btns.addStretch(1)
        recompute = QPushButton("Recompute")
        recompute.clicked.connect(self._render)
        btns.addWidget(recompute)
        self._root.addLayout(btns)
