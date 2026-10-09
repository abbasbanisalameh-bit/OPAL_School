from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
JS = (ROOT / "static/js/opal_erp.js").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "OPAL_UPDATE_MANIFEST.json").read_text(encoding="utf-8"))
RELEASE = (ROOT / "OPAL_RELEASE_NAME.txt").read_text(encoding="utf-8").strip()
BASE = (ROOT / "templates/base/base.html").read_text(encoding="utf-8")
PRINT = (ROOT / "templates/parent_portal/family_statement_print.html").read_text(encoding="utf-8")


def test_r150_metadata_is_sequential_and_based_on_r149():
    assert MANIFEST["package_revision"] == 150
    assert "R149" in MANIFEST["baseline"]
    assert "R150" in RELEASE
    assert MANIFEST["version_name"] == RELEASE


def test_r150_tables_fill_container_and_keep_single_horizontal_line():
    assert "width: max-content !important;" in CSS
    assert "min-width: 100% !important;" in CSS
    assert "max-width: none !important;" in CSS
    assert "white-space: nowrap !important;" in CSS
    assert "overflow-x: auto !important;" in CSS
    assert "overflow-y: auto !important;" in CSS


def test_r150_all_screen_tables_get_a_scroll_wrapper_and_cards_are_disabled():
    assert "opal-universal-table-scroll" in CSS
    assert "body:not([class*='opal-standalone-']) table" in JS
    assert "table.classList.remove(\"opal-mobile-card-table\")" in JS
    assert "wrapper.className = \"opal-universal-table-scroll\"" in JS


def test_r150_preserves_wide_timetable_matrix():
    assert ".opal-main .opal-timetable-matrix-wrap > .opal-timetable-grid" in CSS
    assert "min-width: max-content !important;" in CSS
    assert "touch-action: pan-x pan-y !important;" in CSS


def test_r150_cache_busting_is_updated_and_print_page_is_r150():
    assert "opal-131.7-r150-universal-table-rule" in BASE
    assert "opal-131.7-r150-universal-table-rule" in PRINT


def test_r150_has_no_migrations():
    migration_files = list((ROOT / "core").glob("**/migrations/*.py"))
    assert not any("r150" in p.name.lower() for p in migration_files)


def test_r150_development_center_tables_are_source_wrapped():
    template_root = ROOT / "templates/development_center"
    for path in template_root.rglob("*.html"):
        if "project_print" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        if "<table" in text.lower():
            assert "opal-universal-table-scroll" in text or "table-responsive" in text
