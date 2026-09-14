"""
ui/dialogs/settings_dialog.py
──────────────────────────────
Model & inference settings dialog (checkpoint, device, input size, batch size,
confidence / NMS / max-boxes, toggles) backed by core.settings.Settings, with
named presets. Reports whether changes require re-running detection.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.settings import Settings
from utils.config import RTDETR_MODELS

# Settings whose change requires re-running detection (not just re-filtering).
_REDETECT_KEYS = {"checkpoint", "device", "precision", "input_size",
                  "batch_size", "snap_to_edges", "test_time_augmentation"}


class _Slider(QWidget):
    """A labelled slider that maps an int track to a float value."""

    def __init__(self, lo: float, hi: float, step: float, value: float, fmt="{:.2f}"):
        super().__init__()
        self._lo, self._step, self._fmt = lo, step, fmt
        self._n = round((hi - lo) / step)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self._s = QSlider(Qt.Orientation.Horizontal)
        self._s.setRange(0, self._n)
        self._s.setValue(round((value - lo) / step))
        self._lbl = QLabel(fmt.format(value))
        self._lbl.setMinimumWidth(44)
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._s.valueChanged.connect(lambda _v: self._lbl.setText(fmt.format(self.value())))
        row.addWidget(self._s, 1)
        row.addWidget(self._lbl)

    def value(self) -> float:
        return round(self._lo + self._s.value() * self._step, 4)


class SettingsDialog(QDialog):
    """Edit inference settings; returns needs_redetect() after accept()."""

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model & inference")
        self.setMinimumWidth(460)
        self.settings = settings
        self._before = settings.as_dict()
        self._needs_redetect = False

        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.checkpoint = QComboBox()
        self.checkpoint.addItems(RTDETR_MODELS)
        cur = settings.get("checkpoint")
        if cur not in RTDETR_MODELS:
            self.checkpoint.addItem(cur)
        self.checkpoint.setCurrentText(cur)

        self.device = QComboBox()
        self.device.addItems(["auto", "cpu", "cuda:0"])
        self.device.setCurrentText(settings.get("device"))

        self.precision = QComboBox()
        self.precision.addItems(["fp16", "fp32"])
        self.precision.setCurrentText(settings.get("precision"))

        self.input_size = QComboBox()
        self.input_size.addItems(["512", "640", "800", "960", "1024"])
        self.input_size.setCurrentText(str(settings.get("input_size")))

        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 64)
        self.batch_size.setValue(int(settings.get("batch_size")))

        self.confidence = _Slider(0.05, 0.95, 0.01, float(settings.get("confidence")))
        self.nms_iou = _Slider(0.10, 0.95, 0.01, float(settings.get("nms_iou")))
        self.max_boxes = QSpinBox()
        self.max_boxes.setRange(1, 1000)
        self.max_boxes.setValue(int(settings.get("max_boxes")))

        form.addRow("Checkpoint", self.checkpoint)
        form.addRow("Device", self.device)
        form.addRow("Precision", self.precision)
        form.addRow("Input size", self.input_size)
        form.addRow("Batch size", self.batch_size)
        form.addRow("Confidence", self.confidence)
        form.addRow("NMS IoU", self.nms_iou)
        form.addRow("Max boxes / frame", self.max_boxes)
        root.addLayout(form)

        self.class_agnostic = QCheckBox("Class-agnostic NMS")
        self.class_agnostic.setChecked(bool(settings.get("class_agnostic_nms")))
        self.snap = QCheckBox("Snap boxes to edges (SAM assist)")
        self.snap.setChecked(bool(settings.get("snap_to_edges")))
        self.tta = QCheckBox("Test-time augmentation (3× slower)")
        self.tta.setChecked(bool(settings.get("test_time_augmentation")))
        for cb in (self.class_agnostic, self.snap, self.tta):
            root.addWidget(cb)

        # presets
        preset_row = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("— presets —")
        self.preset_combo.addItems(settings.list_presets())
        self.preset_combo.currentTextChanged.connect(self._load_preset)
        save_preset = QPushButton("Save as preset…")
        save_preset.clicked.connect(self._save_preset)
        preset_row.addWidget(self.preset_combo, 1)
        preset_row.addWidget(save_preset)
        root.addLayout(preset_row)

        hint = QLabel(
            "Changing thresholds re-filters existing detections; changing the "
            "checkpoint, device, or input size requires re-running detection."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#8b909c; font-size:12px;")
        root.addWidget(hint)

        btns = QDialogButtonBox()
        reset = btns.addButton("Reset", QDialogButtonBox.ButtonRole.ResetRole)
        btns.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        apply_btn = btns.addButton("Apply", QDialogButtonBox.ButtonRole.AcceptRole)
        apply_btn.setObjectName("primary")
        reset.clicked.connect(self._reset)
        btns.accepted.connect(self._apply)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    # ── internal ──────────────────────────────────────────────────────────────
    def _collect(self) -> dict:
        return {
            "checkpoint": self.checkpoint.currentText(),
            "device": self.device.currentText(),
            "precision": self.precision.currentText(),
            "input_size": int(self.input_size.currentText()),
            "batch_size": self.batch_size.value(),
            "confidence": self.confidence.value(),
            "nms_iou": self.nms_iou.value(),
            "max_boxes": self.max_boxes.value(),
            "class_agnostic_nms": self.class_agnostic.isChecked(),
            "snap_to_edges": self.snap.isChecked(),
            "test_time_augmentation": self.tta.isChecked(),
        }

    def _apply(self):
        after = self._collect()
        self._needs_redetect = any(
            self._before.get(k) != after.get(k) for k in _REDETECT_KEYS
        )
        self.settings.update(after)
        self.settings.save()
        self.accept()

    def _reset(self):
        self.settings.reset()
        # re-open with defaults
        self.done(2)

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, "Save preset", "Preset name:")
        if ok and name.strip():
            self.settings.update(self._collect())
            self.settings.save_preset(name.strip())
            if self.preset_combo.findText(name.strip()) < 0:
                self.preset_combo.addItem(name.strip())

    def _load_preset(self, name: str):
        if name and not name.startswith("—"):
            self.settings.load_preset(name)
            # reflect loaded values
            self.confidence._s.setValue(
                round((float(self.settings.get("confidence")) - 0.05) / 0.01))
            self.nms_iou._s.setValue(
                round((float(self.settings.get("nms_iou")) - 0.10) / 0.01))
            self.max_boxes.setValue(int(self.settings.get("max_boxes")))
            self.batch_size.setValue(int(self.settings.get("batch_size")))
            self.input_size.setCurrentText(str(self.settings.get("input_size")))
            self.checkpoint.setCurrentText(self.settings.get("checkpoint"))

    def needs_redetect(self) -> bool:
        return self._needs_redetect
