from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'static/css/opal_theme_system.css').read_text(encoding='utf-8')
TEMPLATE = (ROOT / 'templates/timetable/dashboard.html').read_text(encoding='utf-8')


def test_r147_two_axis_scroll_authority():
    assert 'overflow-x: auto !important;' in CSS
    assert 'overflow-y: auto !important;' in CSS
    assert 'touch-action: pan-x pan-y !important;' in CSS
    assert '.opal-main .opal-timetable-matrix-wrap' in CSS
    assert '.opal-main .opal-live-events-matrix-wrap' in CSS


def test_r147_live_events_use_independent_grade_blocks():
    assert 'opal-live-grade-block' in TEMPLATE
    assert 'opal-live-grade-title' in TEMPLATE
    assert 'opal-live-section-head' in TEMPLATE
    assert 'role="region" aria-label="الأحداث الجارية للصفوف والشعب"' in TEMPLATE
