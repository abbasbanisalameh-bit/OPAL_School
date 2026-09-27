import json
from pathlib import Path

from django.test import SimpleTestCase

from core.release_contract_assertions import assert_forward_compatible_release_identity

ROOT = Path(__file__).resolve().parents[1]


class R130ProductionCleanupContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_advances_from_r129(self):
        assert_forward_compatible_release_identity(self, self.source, min_revision=42)
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(manifest["baseline"], "OPAL Update 131.7 R129 - Receipt Content Rendering Repair")
        self.assertEqual(manifest["code_only"], True)

    def test_single_css_authority_and_current_cache_identity(self):
        css_files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.css"))
        self.assertEqual(css_files, ["static/css/opal_theme_system.css"])
        for relative in (
            "templates/base/base.html",
            "templates/registration/auth_base.html",
            "templates/admissions/registration_receipt.html",
            "templates/admissions/fee_payment_receipt.html",
            "templates/students/student_360_print.html",
        ):
            source = self.source(relative)
            self.assertIn("opal-131.7-r130-production-cleanup", source, relative)
            self.assertNotIn("opal-131.7-r129-receipt-content", source, relative)

    def test_global_academic_context_is_read_only(self):
        source = self.source("core/context_processors.py")
        self.assertIn("request_academic_context(request, persist=False)", source)
        self.assertNotIn("request_academic_context(request, persist=True)", source)

    def test_safe_live_status_cache_is_short_lived(self):
        source = self.source("timetable/live_services.py")
        self.assertIn("from django.core.cache import cache", source)
        self.assertIn('cache.set(cache_key, result, 10)', source)
        self.assertIn('cache.get(cache_key)', source)

    def test_teacher_portal_reuses_live_status_in_global_context(self):
        view = self.source("teachers/views.py")
        processor = self.source("timetable/context_processors.py")
        self.assertIn("request._opal_live_schedule = live_status", view)
        self.assertIn('getattr(request, "_opal_live_schedule", None)', processor)

    def test_cleanup_removed_old_per_release_install_notes(self):
        old = [
            "INSTALL_OPAL_UPDATE_131_7_R129_AR.md",
            "OPAL_UPDATE_131_7_R129_RELEASE_NOTES_AR.md",
            "INSTALL_OPAL_UPDATE_131_7_R128_AR.md",
            "OPAL_UPDATE_131_7_R128_RELEASE_NOTES_AR.md",
            "OPAL_UPDATE_131_7_R128_CHANGED_FILES.txt",
        ]
        for relative in old:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_no_runtime_artifacts_are_tracked_in_tree(self):
        forbidden_suffixes = {".pyc", ".pyo", ".bak", ".old", ".orig"}
        forbidden_names = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
        found = []
        for path in ROOT.rglob("*"):
            if any(part in forbidden_names for part in path.parts) or path.suffix.lower() in forbidden_suffixes:
                found.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(found, [], found)
