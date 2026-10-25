from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "OPAL_UPDATE_MANIFEST.json").read_text(encoding="utf-8"))
RELEASE = (ROOT / "OPAL_RELEASE_NAME.txt").read_text(encoding="utf-8").strip()
BASE = (ROOT / "templates/base/base.html").read_text(encoding="utf-8")
CSS = (ROOT / "static/css/opal_theme_system.css").read_text(encoding="utf-8")
TEMPLATE = (ROOT / "templates/core/system_updates.html").read_text(encoding="utf-8")


def test_r154_release_identity_and_manifest_are_aligned():
    assert RELEASE == "OPAL Update 131.7 R154 - Mobile Update Center Repair"
    assert MANIFEST["version"] == "131.7"
    assert MANIFEST["package_revision"] == 154
    assert MANIFEST["version_name"] == RELEASE
    assert MANIFEST["baseline"].endswith("R153 - Sticky Table Header Contrast")
    assert MANIFEST["code_only"] is True


def test_r154_cache_token_is_used_by_shared_css_authority():
    assert "css/opal_theme_system.css" in BASE
    assert "opal-131.7-r154-mobile-update-center" in BASE
    assert "opal-131.7-r153-sticky-table-header" not in BASE


def test_r154_mobile_rules_are_scoped_to_update_center():
    assert "#opal-update-workspace" in CSS
    assert ".opal-update-current-card" in CSS
    assert "@media screen and (max-width: 767.98px)" in CSS
    assert ".opal-update-current-state" in CSS
    assert "min-width: 0;" in CSS
    assert ".opal-update-saved-card .opal-table-viewport" in CSS
    assert 'data-update-source="local"' in TEMPLATE
    assert 'data-update-source="github"' in TEMPLATE
    assert 'name="update_file"' in TEMPLATE


def test_r154_does_not_add_database_migrations_or_parallel_stylesheets():
    assert not list((ROOT / "core" / "migrations").glob("*r154*"))
    assert not (ROOT / "static" / "css" / "opal_update_center_r154.css").exists()


def test_r154_release_notes_state_scope_and_validation_limitations():
    notes = (ROOT / "OPAL_UPDATE_131_7_R154_RELEASE_NOTES_AR.md").read_text(encoding="utf-8")
    assert "لا تغييرات في قاعدة البيانات" in notes
    assert "اختبارات Django" in notes
