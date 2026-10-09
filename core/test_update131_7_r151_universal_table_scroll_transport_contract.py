from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
JS = (ROOT / "static/js/opal_erp.js").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "OPAL_UPDATE_MANIFEST.json").read_text(encoding="utf-8"))
RELEASE = (ROOT / "OPAL_RELEASE_NAME.txt").read_text(encoding="utf-8").strip()
BASE = (ROOT / "templates/base/base.html").read_text(encoding="utf-8")
GROUPS = (ROOT / "transport/templates/transport/groups/list.html").read_text(encoding="utf-8")


def test_r151_metadata_is_sequential_and_based_on_r150():
    assert MANIFEST["package_revision"] == 151
    assert "R150" in MANIFEST["baseline"]
    assert "R151" in RELEASE
    assert MANIFEST["version_name"] == RELEASE


def test_r151_has_bounded_internal_horizontal_and_vertical_scroll():
    assert "overflow-x: auto !important;" in CSS
    assert "overflow-y: auto !important;" in CSS
    assert "max-height: min(70dvh, 760px) !important;" in CSS
    assert "white-space: nowrap !important;" in CSS
    assert "width: max-content !important;" in CSS
    assert "min-width: 100% !important;" in CSS


def test_r151_transport_groups_use_the_unified_member_table():
    assert "opal-transport-members-panel" in GROUPS
    assert "opal-universal-table-scroll" in GROUPS
    assert '<th scope="col">تحديد</th>' in GROUPS
    assert '<th scope="col">الطالب</th>' in GROUPS
    assert '<th scope="col">رقم التسجيل</th>' in GROUPS
    assert 'form="move-{{ group.pk }}"' in GROUPS


def test_r151_transport_member_panel_has_its_own_scroll_limit():
    assert ".opal-main .opal-transport-members-panel .opal-universal-table-scroll" in CSS
    assert "max-height: min(52dvh, 460px) !important;" in CSS


def test_r151_table_wrapper_accessibility_mentions_both_axes():
    assert 'جدول قابل للتمرير أفقيًا وعموديًا' in JS


def test_r151_cache_busting():
    assert "opal-131.7-r151-table-scroll-containment" in BASE


def test_r151_has_no_migrations():
    migration_files = list((ROOT / "core").glob("**/migrations/*.py"))
    assert not any("r151" in p.name.lower() for p in migration_files)
