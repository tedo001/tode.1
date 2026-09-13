"""Tests for core.time_tracker.AnnotationTimer (deterministic fake clock)."""
import os

from core.time_tracker import AnnotationTimer


class _Clock:
    """Manually-advanced clock for deterministic timing tests."""

    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class TestAnnotationTimer:
    def test_active_time_accrues_while_active(self):
        clk = _Clock()
        tm = AnnotationTimer(idle_timeout=30.0, clock=clk)
        tm.start()
        tm.touch(0)
        clk.advance(5)
        tm.tick()
        assert 4.9 < tm.active_seconds < 5.1

    def test_idle_auto_pause(self):
        clk = _Clock()
        tm = AnnotationTimer(idle_timeout=30.0, clock=clk)
        tm.start()
        tm.touch(0)
        clk.advance(300)     # 300s elapse with no activity
        tm.tick()
        # only idle_timeout (30s) is credited after the action, not the full 300
        assert 29.9 < tm.active_seconds < 30.1

    def test_per_frame_timing(self):
        clk = _Clock()
        tm = AnnotationTimer(idle_timeout=30.0, clock=clk)
        tm.start()
        tm.set_frame(0)
        clk.advance(3)
        tm.touch(0)
        tm.set_frame(1)
        clk.advance(7)
        tm.touch(1)
        assert 2.9 < tm.frame_seconds(0) < 3.1
        assert 6.9 < tm.frame_seconds(1) < 7.1

    def test_seed_makes_totals_cumulative(self):
        clk = _Clock()
        tm = AnnotationTimer(clock=clk)
        tm.seed(120.0, {0: 50.0})
        tm.start()
        tm.touch(0)
        clk.advance(4)
        tm.tick()
        assert 123.9 < tm.active_seconds < 124.1     # 120 baseline + 4
        assert 53.9 < tm.frame_seconds(0) < 54.1     # 50 baseline + 4

    def test_save_load_round_trip(self, tmp_path):
        clk = _Clock()
        tm = AnnotationTimer(clock=clk)
        tm.start()
        tm.touch(0)
        clk.advance(8)
        tm.tick()
        p = os.path.join(tmp_path, "timing.json")
        tm.save(p)

        tm2 = AnnotationTimer(clock=_Clock())
        tm2.load(p)
        assert 7.9 < tm2.active_seconds < 8.2

    def test_format_hms(self):
        assert AnnotationTimer.format_hms(65) == "1:05"
        assert AnnotationTimer.format_hms(3725) == "1:02:05"
