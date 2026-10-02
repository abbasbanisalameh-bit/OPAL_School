from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
MANIFEST = (ROOT / "OPAL_UPDATE_MANIFEST.json").read_text(encoding="utf-8")
RELEASE = (ROOT / "OPAL_RELEASE_NAME.txt").read_text(encoding="utf-8")


def test_r148_metadata_is_sequential_and_based_on_r147():
    assert '"package_revision": 148' in MANIFEST
    assert 'R147' in MANIFEST
    assert 'R148' in RELEASE


def test_r148_standard_tables_fill_container_and_keep_two_axis_scroll():
    assert 'width: 100% !important;' in CSS
    assert 'overflow-y: auto !important;' in CSS
    assert 'touch-action: pan-x pan-y !important;' in CSS
    assert 'border-collapse: collapse !important;' in CSS
    assert 'min-width: 100% !important;' in CSS


def test_r148_live_grade_blocks_fill_container():
    assert '.opal-main .opal-live-grade-block' in CSS
    assert '.opal-main .opal-live-events-matrix' in CSS
    assert 'table-layout: fixed !important;' in CSS
