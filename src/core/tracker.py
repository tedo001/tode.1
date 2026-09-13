"""
core/tracker.py
────────────────
Kalman-filter multi-object tracking via Roboflow **supervision.ByteTrack**.

Used (opt-in) by ``AnnotationManager.auto_annotate_all`` on video sources to
give per-object track ids that are temporally consistent across frames — the
Kalman filter smooths jitter and bridges short detection gaps, which makes the
auto-annotations more stable and accurate than independent per-frame detection.

``supervision`` (and its ``scipy`` dependency) is imported lazily so importing
this module stays cheap and the rest of the app never hard-requires it.
"""
from __future__ import annotations

import numpy as np

from models.annotation_model import BoundingBox
from utils.logger import get_logger

log = get_logger("core.FrameTracker")


class FrameTracker:
    """Thin wrapper over ``supervision.ByteTrack`` that speaks ``BoundingBox``."""

    def __init__(
        self,
        frame_rate: float = 30.0,
        track_activation_threshold: float = 0.25,
        lost_track_buffer: int = 30,
        minimum_matching_threshold: float = 0.8,
    ):
        import supervision as sv  # lazy: pulls scipy
        self._sv = sv
        self._tracker = sv.ByteTrack(
            track_activation_threshold=track_activation_threshold,
            lost_track_buffer=lost_track_buffer,
            minimum_matching_threshold=minimum_matching_threshold,
            frame_rate=frame_rate,
        )
        log.info(
            f"[ByteTrack] tracker ready — fps={frame_rate}, "
            f"activation={track_activation_threshold}, buffer={lost_track_buffer}"
        )

    def reset(self) -> None:
        """Clear tracker state (call before tracking a new sequence)."""
        self._tracker.reset()

    def _empty_detections(self):
        """A typed-empty Detections so ByteTrack can advance on frames with no
        detections (Detections.empty() has confidence=None which ByteTrack
        rejects)."""
        return self._sv.Detections(
            xyxy=np.empty((0, 4), dtype=np.float32),
            confidence=np.array([], dtype=np.float32),
            class_id=np.array([], dtype=int),
        )

    def update(self, boxes: list[BoundingBox], img_w: int, img_h: int) -> list[BoundingBox]:
        """Advance the tracker by one frame and return boxes carrying track ids.

        ``boxes`` are normalised BoundingBoxes for the current frame. Returns the
        tracked subset (ByteTrack drops detections it cannot confirm) as new
        normalised BoundingBoxes with ``track_id`` set.
        """
        if img_w <= 0 or img_h <= 0:
            return boxes
        if not boxes:
            self._tracker.update_with_detections(self._empty_detections())
            return []

        names = {b.class_id: b.class_name for b in boxes}
        xyxy = np.array(
            [
                [
                    (b.x_center - b.width / 2) * img_w,
                    (b.y_center - b.height / 2) * img_h,
                    (b.x_center + b.width / 2) * img_w,
                    (b.y_center + b.height / 2) * img_h,
                ]
                for b in boxes
            ],
            dtype=np.float32,
        )
        conf = np.array([b.confidence for b in boxes], dtype=np.float32)
        cls = np.array([b.class_id for b in boxes], dtype=int)

        dets = self._sv.Detections(xyxy=xyxy, confidence=conf, class_id=cls)
        tracked = self._tracker.update_with_detections(dets)

        out: list[BoundingBox] = []
        for (x1, y1, x2, y2), c, cid, tid in zip(
            tracked.xyxy, tracked.confidence, tracked.class_id, tracked.tracker_id,
            strict=False,
        ):
            cid = int(cid)
            out.append(BoundingBox(
                class_id   = cid,
                class_name = names.get(cid, str(cid)),
                x_center   = ((x1 + x2) / 2) / img_w,
                y_center   = ((y1 + y2) / 2) / img_h,
                width      = (x2 - x1)       / img_w,
                height     = (y2 - y1)       / img_h,
                confidence = float(c),
                track_id   = int(tid),
            ))
        return out
