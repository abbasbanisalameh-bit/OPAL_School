from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "OPAL_UPDATE_MANIFEST.json").read_text(encoding="utf-8"))
RELEASE = (ROOT / "OPAL_RELEASE_NAME.txt").read_text(encoding="utf-8").strip()
BASE = (ROOT / "templates/base/base.html").read_text(encoding="utf-8")


def test_r149_metadata_is_sequential_and_based_on_r148():
    assert MANIFEST["package_revision"] == 149
    assert "R148" in MANIFEST["baseline"]
    assert "R149" in RELEASE
    assert MANIFEST["version_name"] == RELEASE


def test_r149_standard_tables_are_full_bleed_and_wrappable_on_mobile():
    assert "width: 100% !important;" in CSS
    assert "min-width: 100% !important;" in CSS
    assert "max-width: 100% !important;" in CSS
    assert "white-space: normal !important;" in CSS
    assert "overflow-wrap: anywhere !important;" in CSS


def test_r149_preserves_wide_timetable_matrix_and_two_axis_touch_scroll():
    assert ".opal-main .opal-timetable-matrix-wrap > .opal-timetable-grid" in CSS
    assert "width: max-content !important;" in CSS
    assert "overflow-x: auto !important;" in CSS
    assert "overflow-y: auto !important;" in CSS
    assert "touch-action: pan-x pan-y !important;" in CSS


def test_r149_cache_busting_is_updated():
    assert "opal-131.7-r149-table-containment" in BASE
