"""
ui/qt_main_window.py
─────────────────────
PySide6 main window for tode. A thin controller over the headless core:

    QMainWindow ── AnnotationCanvas
        │
        ├── LoadWorker   → AnnotationManager (video / image / folder)
        ├── DetectWorker → AutoAnnotator (RT-DETR) → boxes
        └── DatasetExporter (YOLO / COCO)

Every UI action maps onto an AnnotationManager call; the manager owns all state.
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.audit_log import audit_log_path, get_audit_log
from core.exporter import DatasetExporter
from core.time_tracker import AnnotationTimer
from models.annotation_model import BoundingBox, ImageClassification, PolygonAnnotation
from ui.qt_canvas import DRAW, POLYGON, VIEW, AnnotationCanvas
from ui.qt_workers import DetectWorker, LoadWorker
from utils.config import RTDETR_DEFAULT_MODEL, RTDETR_MODELS
from utils.logger import get_logger

log = get_logger("ui.qt_main_window")

_VIDEO_EXTS = "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv"
_IMAGE_EXTS = "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp"


class TodeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("tode — RT-DETR annotation")
        self.resize(1280, 820)

        self.manager = None
        self.current_index = 0
        self._indices: list[int] = []
        self._class_ids: dict[str, int] = {}
        self._busy = False
        self._worker = None
        self.timer = AnnotationTimer()
        self.audit = get_audit_log()
        self.audit.record("app_start", model=RTDETR_DEFAULT_MODEL)

        self._build_ui()
        self._build_shortcuts()

        # 1 Hz clock: accrue active annotation time and refresh the readout.
        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._tick_clock)
        self._clock_timer.start()

        log.info("Qt main window ready")

    # ── construction ──────────────────────────────────────────────────────────
    def _build_ui(self):
        self.canvas = AnnotationCanvas()
        self.canvas.boxDrawn.connect(self._on_box_drawn)
        self.canvas.boxEdited.connect(self._on_box_edited)
        self.canvas.boxSelected.connect(self._on_box_selected)
        self.canvas.polygonDrawn.connect(self._on_polygon_drawn)
        self.canvas.openRequested.connect(self._open_source)

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(6, 6, 6, 6)

        # left: canvas + frame nav
        left = QVBoxLayout()
        left.addWidget(self.canvas, 1)
        nav = QHBoxLayout()
        self.prev_btn = QPushButton("◀ Prev")
        self.next_btn = QPushButton("Next ▶")
        self.prev_btn.clicked.connect(lambda: self._nav(-1))
        self.next_btn.clicked.connect(lambda: self._nav(+1))
        self.frame_slider = QSlider(Qt.Orientation.Horizontal)
        self.frame_slider.valueChanged.connect(self._on_slider)
        self.counter = QLabel("Frame 0 / 0")
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.frame_slider, 1)
        nav.addWidget(self.next_btn)
        nav.addWidget(self.counter)
        left.addLayout(nav)
        root.addLayout(left, 1)

        # right: control panel
        root.addWidget(self._build_panel())

        self.setCentralWidget(central)
        self._build_toolbar()

        self.status = self.statusBar()
        self.time_label = QLabel("⏱ 0:00")
        self.time_label.setToolTip("Active annotation time (auto-pauses when idle) · time on current frame")
        self.status.addPermanentWidget(self.time_label)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.progress.hide()
        self.status.addPermanentWidget(self.progress)
        self._set_status("No source loaded — open a video, image, or folder.")

    def _build_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(280)
        v = QVBoxLayout(panel)

        v.addWidget(QLabel("<b>Mode</b>"))
        mode_row = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["View (V)", "Draw box (W)", "Polygon"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        mode_row.addWidget(self.mode_combo)
        v.addLayout(mode_row)

        v.addWidget(QLabel("<b>RT-DETR model</b>"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(RTDETR_MODELS)
        self.model_combo.setCurrentText(RTDETR_DEFAULT_MODEL)
        self.model_combo.currentTextChanged.connect(self._on_model_change)
        v.addWidget(self.model_combo)

        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel("Confidence"))
        self.conf_spin = QDoubleSpinBox()
        self.conf_spin.setRange(0.05, 0.95)
        self.conf_spin.setSingleStep(0.05)
        self.conf_spin.setValue(0.45)
        self.conf_spin.valueChanged.connect(self._on_conf_change)
        conf_row.addWidget(self.conf_spin)
        v.addLayout(conf_row)

        self.detect_btn = QPushButton("⚡ Detect Frame")
        self.detect_all_btn = QPushButton("🔁 Detect All Frames")
        self.detect_btn.clicked.connect(self._run_detect)
        self.detect_all_btn.clicked.connect(self._run_detect_all)
        v.addWidget(self.detect_btn)
        v.addWidget(self.detect_all_btn)

        self.track_check = QCheckBox("Track across frames (ByteTrack + Kalman)")
        self.track_check.setToolTip(
            "Detect All only: link detections across frames with ByteTrack for "
            "temporally-consistent, smoother annotations."
        )
        v.addWidget(self.track_check)

        v.addWidget(QLabel("<b>Class for new box</b>"))
        self.class_edit = QLineEdit("object")
        v.addWidget(self.class_edit)

        v.addWidget(QLabel("<b>Annotations</b>"))
        self.box_list = QListWidget()
        self.box_list.currentRowChanged.connect(self._on_list_row)
        v.addWidget(self.box_list, 1)

        del_row = QHBoxLayout()
        self.del_btn = QPushButton("🗑 Delete")
        self.clear_btn = QPushButton("Clear frame")
        self.del_btn.clicked.connect(self._delete_selected_box)
        self.clear_btn.clicked.connect(self._clear_frame)
        del_row.addWidget(self.del_btn)
        del_row.addWidget(self.clear_btn)
        v.addLayout(del_row)

        self.classify_btn = QPushButton("🏷 Classify frame")
        self.classify_btn.clicked.connect(self._classify_frame)
        v.addWidget(self.classify_btn)

        return panel

    def _build_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)

        def act(text, slot, shortcut=None):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            tb.addAction(a)
            return a

        act("📂 Open", self._open_source, "Ctrl+O")
        act("🎬 Video", self._open_video)
        act("🖼 Image", self._open_image)
        act("📁 Folder", self._open_folder)
        tb.addSeparator()
        act("💾 Save", self._save, "Ctrl+S")
        act("📤 Export", self._export, "Ctrl+E")
        tb.addSeparator()
        act("📋 Logs", self._show_logs)

    def _build_shortcuts(self):
        specs = {
            "A": lambda: self._nav(-1), "Left": lambda: self._nav(-1),
            "D": lambda: self._nav(+1), "Right": lambda: self._nav(+1),
            "Home": lambda: self._nav("first"), "End": lambda: self._nav("last"),
            "W": lambda: self.mode_combo.setCurrentIndex(1),
            "V": lambda: self.mode_combo.setCurrentIndex(0),
            "Y": self._run_detect,
            "Delete": self._clear_frame,
        }
        for key, fn in specs.items():
            a = QAction(self)
            a.setShortcut(QKeySequence(key))
            a.triggered.connect(fn)
            self.addAction(a)

    # ── source opening ──────────────────────────────────────────────────────
    def _open_source(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open video or image", "",
            f"Media ({_VIDEO_EXTS} {_IMAGE_EXTS})",
        )
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}:
            self._open_video(path)
        else:
            self._start_load("image", path)

    def _open_video(self, path: str | None = None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open video", "", f"Video ({_VIDEO_EXTS})")
        if not path:
            return
        step, ok = QInputDialog.getInt(self, "Frame step", "Load every N-th frame:", 1, 1, 30)
        if not ok:
            step = 1
        self._start_load("video", path, step)

    def _open_image(self, path: str | None = None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open image", "", f"Image ({_IMAGE_EXTS})")
        if path:
            self._start_load("image", path)

    def _open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Open image folder")
        if path:
            self._start_load("image_folder", path)

    def _start_load(self, source_type: str, path: str, step: int = 1):
        if self._busy:
            return
        self._set_busy(True, f"Loading {os.path.basename(path)}…")
        self._worker = LoadWorker(source_type, path, step)
        self._worker.progress.connect(self._on_progress)
        self._worker.done.connect(self._on_loaded)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_loaded(self, manager):
        self.manager = manager
        self._indices = manager.all_frame_indices()
        self.current_index = 0
        self._set_busy(False)
        # Fresh timer for this project; carry over prior time if it exists.
        self.timer = AnnotationTimer()
        self.timer.load(self._timing_path())
        self.timer.start()
        # Route audit entries into this project's own audit.jsonl too.
        base = getattr(getattr(manager, "l_store", None), "base_dir", None)
        self.audit.set_project_sink(os.path.join(base, "audit.jsonl") if base else None)
        self.audit.record(
            "source_loaded",
            target=getattr(getattr(manager, "l_store", None), "video_name", "?"),
            frames=len(self._indices),
        )
        self.frame_slider.setMaximum(max(0, len(self._indices) - 1))
        self._show_frame(0)
        self._set_status(f"Loaded {len(self._indices)} frame(s).")

    def _timing_path(self) -> str:
        base = getattr(getattr(self.manager, "l_store", None), "base_dir", ".")
        return os.path.join(base, "timing.json")

    # ── frame display ─────────────────────────────────────────────────────────
    def _show_frame(self, pos: int):
        if not self.manager or not self._indices:
            return
        pos = max(0, min(pos, len(self._indices) - 1))
        self.current_index = pos
        idx = self._indices[pos]
        self.timer.set_frame(idx)
        ann = self.manager.get_annotation(idx)
        frame = self.manager._read_frame_reliable(ann, idx) if ann else None
        self.canvas.set_image_bgr(frame)
        self.canvas.set_boxes(ann.boxes if ann else [], selected=-1)
        self.canvas.set_polygons(ann.polygons if ann else [])
        self.counter.setText(f"Frame {pos + 1} / {len(self._indices)}")
        self.frame_slider.blockSignals(True)
        self.frame_slider.setValue(pos)
        self.frame_slider.blockSignals(False)
        self._refresh_box_list()

    def _refresh_box_list(self):
        self.box_list.blockSignals(True)
        self.box_list.clear()
        ann = self._current_ann()
        if ann:
            for i, b in enumerate(ann.boxes):
                src = "AUTO" if b.confidence < 1.0 else "MAN "
                self.box_list.addItem(f"[{i:02d}] {src} {b.class_name}")
        self.box_list.blockSignals(False)

    def _current_ann(self):
        if not self.manager or not self._indices:
            return None
        return self.manager.get_annotation(self._indices[self.current_index])

    def _nav(self, where):
        if not self._indices:
            return
        if where == "first":
            self._show_frame(0)
        elif where == "last":
            self._show_frame(len(self._indices) - 1)
        else:
            self._show_frame(self.current_index + int(where))

    def _on_slider(self, value):
        self._show_frame(value)

    # ── mode ──────────────────────────────────────────────────────────────────
    def _on_mode_change(self, index: int):
        self.canvas.set_mode({0: VIEW, 1: DRAW, 2: POLYGON}.get(index, VIEW))

    # ── box operations (mapped to AnnotationManager) ───────────────────────────
    def _class_id_for(self, name: str) -> int:
        name = name.strip() or "object"
        if name not in self._class_ids:
            self._class_ids[name] = len(self._class_ids)
        return self._class_ids[name]

    def _on_box_drawn(self, cx, cy, w, h):
        ann = self._current_ann()
        if not ann:
            return
        self.timer.touch()
        name = self.class_edit.text().strip() or "object"
        box = BoundingBox(self._class_id_for(name), name, cx, cy, w, h, 1.0)
        self.manager.add_box(ann.frame_index, box)
        self.audit.record("box_added", target=f"frame:{ann.frame_index}", cls=name)
        self.canvas.set_boxes(ann.boxes, selected=len(ann.boxes) - 1)
        self._refresh_box_list()

    def _on_box_edited(self, index, cx, cy, w, h):
        # The canvas mutated the BoundingBox object in place; just refresh views.
        self.timer.touch()
        ann = self._current_ann()
        if ann:
            self.audit.record("box_edited", target=f"frame:{ann.frame_index}", index=index)
        self._refresh_box_list()

    def _on_box_selected(self, index):
        self.box_list.blockSignals(True)
        self.box_list.setCurrentRow(index)
        self.box_list.blockSignals(False)

    def _on_list_row(self, row):
        self.canvas.set_selected(row)

    def _delete_selected_box(self):
        ann = self._current_ann()
        row = self.box_list.currentRow()
        if ann and 0 <= row < len(ann.boxes):
            self.timer.touch()
            self.manager.remove_box(ann.frame_index, row)
            self.audit.record("box_deleted", target=f"frame:{ann.frame_index}", index=row)
            self.canvas.set_boxes(ann.boxes, selected=-1)
            self._refresh_box_list()

    def _clear_frame(self):
        ann = self._current_ann()
        if ann:
            self.manager.clear_frame(ann.frame_index)
            self.audit.record("frame_cleared", target=f"frame:{ann.frame_index}")
            self.canvas.set_boxes(ann.boxes, selected=-1)
            self._refresh_box_list()

    def _on_polygon_drawn(self, points):
        ann = self._current_ann()
        if not ann:
            return
        self.timer.touch()
        name = self.class_edit.text().strip() or "object"
        poly = PolygonAnnotation(self._class_id_for(name), name, points, 1.0)
        self.manager.add_polygon(ann.frame_index, poly)
        self.audit.record(
            "polygon_added", target=f"frame:{ann.frame_index}", cls=name, points=len(points)
        )
        self.canvas.set_polygons(ann.polygons)

    def _classify_frame(self):
        ann = self._current_ann()
        if not ann:
            return
        self.timer.touch()
        name = self.class_edit.text().strip() or "object"
        self.manager.set_classification(
            ann.frame_index, ImageClassification(self._class_id_for(name), name, 1.0)
        )
        self.audit.record("frame_classified", target=f"frame:{ann.frame_index}", cls=name)
        self._set_status(f"Frame classified as '{name}'.")

    # ── RT-DETR detection ─────────────────────────────────────────────────────
    def _run_detect(self):
        ann = self._current_ann()
        if not ann or self._busy:
            return
        self._set_busy(True, "Running RT-DETR on this frame…")
        self._worker = DetectWorker(
            self.manager, ann.frame_index, self.conf_spin.value(),
            model_id=self.model_combo.currentText(),
        )
        self._worker.status.connect(self._set_status)
        self._worker.done.connect(self._on_detect_one)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_detect_one(self, idx):
        self._set_busy(False)
        self._show_frame(self.current_index)
        ann = self._current_ann()
        n = len(ann.boxes) if ann else 0
        self._seed_classes_from_model()
        self.audit.record(
            "detect_frame", target=f"frame:{idx}", boxes=n,
            model=self.model_combo.currentText(),
        )
        self._set_status(f"RT-DETR: {n} object(s).")

    def _run_detect_all(self):
        if not self.manager or self._busy:
            return
        self._set_busy(True, "Running RT-DETR on all frames…")
        self._worker = DetectWorker(
            self.manager, None, self.conf_spin.value(),
            model_id=self.model_combo.currentText(),
            track=self.track_check.isChecked(),
        )
        self._worker.status.connect(self._set_status)
        self._worker.progress.connect(self._on_progress)
        self._worker.done.connect(self._on_detect_all)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_detect_all(self, count):
        self._set_busy(False)
        self._seed_classes_from_model()
        self._show_frame(self.current_index)
        self.audit.record(
            "detect_all", annotated=count, total=self.manager.total_count,
            model=self.model_combo.currentText(), track=self.track_check.isChecked(),
        )
        self._set_status(f"RT-DETR complete — {count}/{self.manager.total_count} annotated.")

    def _seed_classes_from_model(self):
        if self.manager:
            for cid, cname in self.manager.detector.class_names.items():
                self._class_ids.setdefault(cname, cid)

    def _on_conf_change(self):
        if self.manager:
            self.manager.detector.confidence = self.conf_spin.value()

    def _on_model_change(self, model: str):
        # Non-blocking: the DetectWorker loads (and downloads if missing) the
        # selected model on the next Detect click, off the UI thread — so
        # switching models never freezes the window during a download.
        self._set_status(f"Model '{model}' selected — loads on next detect.")

    # ── save / export ─────────────────────────────────────────────────────────
    def _save(self):
        if not self.manager:
            return
        self.manager.save_annotations()
        try:
            self.timer.save(self._timing_path())
        except OSError as exc:            # noqa: BLE001 - saving time is best-effort
            log.warning(f"Could not save timing: {exc}")
        self.audit.record(
            "annotations_saved",
            annotated=self.manager.annotated_count,
            active_seconds=round(self.timer.active_seconds, 1),
        )
        mins = self.timer.active_seconds / 60
        self._set_status(f"Annotations saved · {mins:.1f} min active annotation time.")

    def _export(self):
        if not self.manager:
            return
        fmt, ok = QInputDialog.getItem(
            self, "Export dataset", "Format:", ["yolo", "coco"], 0, False
        )
        if not ok:
            return
        out = QFileDialog.getExistingDirectory(self, "Export destination")
        if not out:
            return
        try:
            summary = DatasetExporter(
                self.manager._annotations,
                self.manager.detector.class_names or {v: k for k, v in self._class_ids.items()},
                out,
            ).export(fmt)
            self.audit.record(
                "dataset_exported", target=out, fmt=fmt, images=summary.get("images"),
            )
            QMessageBox.information(
                self, "Export complete",
                f"Exported {summary.get('images', '?')} image(s) as {fmt.upper()} to:\n{out}",
            )
        except Exception as exc:          # noqa: BLE001
            self.audit.record("export_failed", target=out, fmt=fmt, error=str(exc))
            QMessageBox.critical(self, "Export failed", str(exc))

    def _show_logs(self):
        from utils.logger import get_log_file_path
        msg = (
            "System log (diagnostics):\n"
            f"{get_log_file_path()}\n\n"
            "Audit log (who did what — JSON Lines):\n"
            f"{audit_log_path()}\n\n"
            "A per-project audit.jsonl is also written next to the project's labels."
        )
        QMessageBox.information(self, "Logs", msg)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _on_progress(self, done, total):
        self.progress.setRange(0, total)
        self.progress.setValue(done)
        self._set_status(f"Detecting… {done}/{total} frames")

    def _set_busy(self, busy: bool, msg: str = ""):
        self._busy = busy
        self.progress.setVisible(busy)
        if busy:
            self.progress.setRange(0, 0)
            if msg:
                self._set_status(msg)
        else:
            self.progress.setRange(0, 100)

    def _on_worker_error(self, msg: str):
        self._set_busy(False)
        QMessageBox.critical(self, "Error", msg)
        self._set_status("Error — see dialog.")

    def _set_status(self, text: str):
        self.status.showMessage(text)

    # ── time tracking ───────────────────────────────────────────────────────────
    def _tick_clock(self):
        """1 Hz: accrue active time and refresh the readout."""
        self.timer.tick()
        self._update_time_label()

    def _update_time_label(self):
        total = AnnotationTimer.format_hms(self.timer.active_seconds)
        if self.manager and self._indices:
            idx = self._indices[self.current_index]
            frame_s = self.timer.frame_seconds(idx)
            self.time_label.setText(f"⏱ {total} · frame {frame_s:.0f}s")
        else:
            self.time_label.setText(f"⏱ {total}")

    def closeEvent(self, event):
        """Persist timing and record the session end on window close."""
        try:
            if self.manager:
                self.timer.save(self._timing_path())
        except OSError:
            pass
        self.audit.record("app_exit", active_seconds=round(self.timer.active_seconds, 1))
        super().closeEvent(event)
