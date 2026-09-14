"""Tests for core.settings.Settings (persisted JSON + presets)."""
import os

from core.settings import DEFAULTS, Settings


class TestSettings:
    def test_defaults_loaded_when_no_file(self, tmp_path):
        s = Settings(path=os.path.join(tmp_path, "settings.json"))
        assert s.get("confidence") == DEFAULTS["confidence"]
        assert s.get("input_size") == DEFAULTS["input_size"]

    def test_set_save_load_roundtrip(self, tmp_path):
        p = os.path.join(tmp_path, "settings.json")
        s = Settings(path=p)
        s.set("confidence", 0.14)
        s.set("batch_size", 16)
        s.save()

        s2 = Settings(path=p)
        assert s2.get("confidence") == 0.14
        assert s2.get("batch_size") == 16

    def test_unknown_key_falls_back_to_default_or_none(self, tmp_path):
        s = Settings(path=os.path.join(tmp_path, "settings.json"))
        assert s.get("does_not_exist") is None
        assert s.get("does_not_exist", 7) == 7

    def test_new_default_keys_merge_over_old_file(self, tmp_path):
        p = os.path.join(tmp_path, "settings.json")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write('{"confidence": 0.2}')      # old file missing newer keys
        s = Settings(path=p)
        assert s.get("confidence") == 0.2
        assert s.get("max_boxes") == DEFAULTS["max_boxes"]   # merged from defaults

    def test_reset(self, tmp_path):
        s = Settings(path=os.path.join(tmp_path, "settings.json"))
        s.set("confidence", 0.99)
        s.reset()
        assert s.get("confidence") == DEFAULTS["confidence"]

    def test_presets(self, tmp_path):
        s = Settings(path=os.path.join(tmp_path, "settings.json"))
        s.set("confidence", 0.14)
        s.set("input_size", 800)
        s.save_preset("driving-default")
        assert "driving-default" in s.list_presets()

        s.reset()
        assert s.get("confidence") == DEFAULTS["confidence"]
        s.load_preset("driving-default")
        assert s.get("confidence") == 0.14
        assert s.get("input_size") == 800
