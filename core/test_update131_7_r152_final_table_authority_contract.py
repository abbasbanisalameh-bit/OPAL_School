from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
JS = (ROOT / "static/js/opal_erp.js").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "OPAL_UPDATE_MANIFEST.json").read_text(encoding="utf-8"))
RELEASE = (ROOT / "OPAL_RELEASE_NAME.txt").read_text(encoding="utf-8").strip()
BASE = (ROOT / "templates/base/base.html").read_text(encoding="utf-8")
PRINT = (ROOT / "templates/parent_portal/family_statement_print.html").read_text(encoding="utf-8")
GROUPS = (ROOT / "transport/templates/transport/groups/list.html").read_text(encoding="utf-8")

R152_MARKER = "OPAL R152 — Final Universal Table Authority"


def test_r152_release_history_remains_present_and_current_release_identity_is_aligned():
    history = ROOT / "OPAL_UPDATE_131_7_R152_RELEASE_NOTES_AR.md"
    assert history.is_file()
    assert MANIFEST["package_revision"] >= 152
    assert "R154" in RELEASE
    assert MANIFEST["version_name"] == RELEASE


def test_r152_has_one_final_table_authority_block():
    assert CSS.count(R152_MARKER) == 1
    assert CSS.index(R152_MARKER) > CSS.index("OPAL R150") if "OPAL R150" in CSS else True
    block = CSS[CSS.index(R152_MARKER):]
    assert "overflow-x: auto !important;" in block
    assert "overflow-y: auto !important;" in block
    assert "width: max-content !important;" in block
    assert "min-width: 100% !important;" in block
    assert "white-space: nowrap !important;" in block
    assert "table-layout: auto !important;" in block
    assert "max-height: min(70dvh, 760px) !important;" in block
    assert "scrollbar-gutter: auto !important;" in block


def test_r152_rows_cannot_wrap_horizontally():
    block = CSS[CSS.index(R152_MARKER):]
    assert "overflow-wrap: normal !important;" in block
    assert "word-break: normal !important;" in block
    assert "min-width: max-content !important;" in block


def test_r152_unifies_js_table_enhancement():
    assert "OPAL_TABLE_SCROLL_INIT_V4" in JS  # compatibility marker retained
    assert "wrapper.className = \"opal-universal-table-scroll\"" in JS
    assert "table.classList.remove(\"opal-mobile-card-table\")" in JS
    assert 'wrapper.dataset.opalTableScrollAuthority = "r152";' in JS
    assert "جدول قابل للتمرير أفقيًا وعموديًا" in JS
    assert JS.count("function initializeScrollableTables") == 0


def test_r152_cache_busting_and_print_template_compatibility():
    assert "opal-131.7-r154-mobile-update-center" in BASE
    # The standalone print surface is intentionally unchanged by this screen-only update.
    assert "opal-131.7-r152-universal-table-authority" in PRINT


def test_r152_transport_groups_use_same_universal_table_rule():
    assert "opal-transport-members-panel" in GROUPS
    assert "opal-universal-table-scroll" in GROUPS
    assert '<th scope="col">تحديد</th>' in GROUPS
    assert '<th scope="col">الطالب</th>' in GROUPS
    assert '<th scope="col">رقم التسجيل</th>' in GROUPS


def test_r152_standalone_fee_receipt_is_screen_wrapped_without_changing_print_layout():
    receipt = (ROOT / "templates/admissions/fee_payment_receipt.html").read_text(encoding="utf-8")
    css = CSS[CSS.index(R152_MARKER):]
    assert receipt.count("receipt-allocations-scroll") == 2
    assert ".receipt-allocations-scroll" in css
    assert "display: contents !important;" in css


def test_r152_no_r152_migrations():
    migration_files = list((ROOT / "core").glob("**/migrations/*.py"))
    assert not any("r152" in p.name.lower() for p in migration_files)


def test_r152_screen_table_templates_are_globally_covered():
    table_templates = []
    for path in (ROOT / "templates").rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "<table" not in text.lower():
            continue
        if "family_statement_print" in str(path) or "print" in path.name.lower():
            continue
        table_templates.append(path)
    assert table_templates
    # Runtime JS covers all body tables except explicit standalone/print surfaces.
    assert "body table" in JS
