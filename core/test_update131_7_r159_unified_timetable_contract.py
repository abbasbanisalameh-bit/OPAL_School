"""R159 contract: timetable administration, official matrix, and live events share one screen."""
from pathlib import Path
import ast
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class R159UnifiedTimetableContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_one_canonical_template_contains_live_matrix_official_grid_and_builder(self):
        page = self.read("templates/timetable/dashboard.html")
        self.assertIn("opal-live-events-matrix", page)
        self.assertIn("opal-print-timetable", page)
        self.assertIn("opal-timetable-grid", page)
        self.assertIn('id="smart-builder"', page)
        self.assertIn('class="opal-card mb-4 opal-screen-only" id="smart-builder"', page)
        self.assertIn("data-live-seconds", page)
        self.assertEqual(page.count("data-live-seconds"), 1)
        self.assertFalse((ROOT / "templates/timetable/overview.html").exists())

    def test_legacy_overview_url_redirects_to_the_canonical_dashboard(self):
        urls = self.read("timetable/urls.py")
        views = self.read("timetable/views.py")
        self.assertIn('path("overview/", views.overview, name="overview")', urls)
        method = views.split("def overview(request):", 1)[1].split("\n\n@management_required", 1)[0]
        self.assertIn('reverse("timetable:dashboard")', method)
        self.assertIn("request.GET.urlencode()", method)
        self.assertIn("HttpResponseRedirect", method)
        self.assertNotIn('render(request, "timetable/overview.html"', method)

    def test_navigation_has_one_timetable_entry(self):
        catalog = self.read("core/workflow_catalog.py")
        contracts = self.read("core/single_entry_contracts.py")
        self.assertIn('"الجدول الأسبوعي", "items": ("timetable",)', catalog)
        self.assertNotIn('"timetable-overview"', catalog)
        self.assertNotIn('"timetable-overview"', contracts)

    def test_system_check_requires_unified_screen_and_no_parallel_template(self):
        checks = self.read("core/checks.py")
        self.assertIn("TIMETABLE_UNIFIED_VIEW_INCOMPLETE", checks)
        self.assertIn("TIMETABLE_PARALLEL_TEMPLATE_PRESENT", checks)
        self.assertIn('"templates/timetable/dashboard.html"', checks)

    def test_refresh_is_owned_by_one_guarded_global_handler(self):
        js = self.read("static/js/opal_erp.js")
        dashboard = self.read("templates/timetable/dashboard.html")
        base = self.read("templates/base/base.html")
        self.assertIn("Number.isFinite(value) && value > 0", js)
        self.assertIn("if (!futureBoundaries.length) return;", js)
        self.assertIn("Live-boundary refresh is handled once", dashboard)
        self.assertNotIn("window.location.reload()", dashboard)
        self.assertNotIn("else window.location.reload()", base)

    def test_release_identity_and_cache_keys(self):
        manifest = json.loads(self.read("OPAL_UPDATE_MANIFEST.json"))
        release_name = self.read("OPAL_RELEASE_NAME.txt").strip()
        self.assertEqual(manifest["version"], self.read("OPAL_VERSION.txt").strip())
        self.assertEqual(manifest["package_revision"], 159)
        self.assertEqual(manifest["version_name"], release_name)
        self.assertTrue(release_name.startswith("OPAL Update 131.7 R159 - "))
        base = self.read("templates/base/base.html")
        self.assertIn("r159-unified-timetable-workspace", base)

    def test_source_validator_enforces_the_unified_screen(self):
        validator = self.read("tools/validate_opal_update_131_source.py")
        self.assertIn('"unified_timetable_workspace"', validator)
        self.assertIn('"parallel_timetable_template_removed"', validator)
        self.assertIn('"legacy_overview_redirects_to_dashboard"', validator)
        self.assertIn("timetable_search_off", validator)
        self.assertNotIn('timetable_overview = require_file("templates/timetable/overview.html")', validator)

    def test_modified_python_files_parse(self):
        for relative in (
            "timetable/views.py",
            "timetable/urls.py",
            "core/checks.py",
            "core/single_entry_contracts.py",
            "core/workflow_catalog.py",
            "tools/validate_opal_update_131_source.py",
        ):
            ast.parse(self.read(relative), filename=relative)


if __name__ == "__main__":
    unittest.main(verbosity=2)
