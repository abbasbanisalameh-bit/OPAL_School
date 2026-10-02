import json
from pathlib import Path

from django.test import SimpleTestCase


ROOT = Path(__file__).resolve().parents[1]


class R143UIConsistencyContractTests(SimpleTestCase):
    def source(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_release_identity_advances_from_r142(self):
        release = self.source("OPAL_RELEASE_NAME.txt").strip()
        manifest = json.loads(self.source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(
            release,
            "OPAL Update 131.7 R143 - System UI Consistency & CSS Guard",
        )
        self.assertEqual(manifest["version_name"], release)
        self.assertEqual(
            manifest["baseline"],
            "OPAL Update 131.7 R142 - Search Surface & Full-Width Glass Table Cleanup",
        )
        self.assertEqual(manifest["package_revision"], 143)

    def test_mobile_ordinary_tables_are_not_forced_wide(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn(".opal-main table {", css)
        self.assertIn("min-width: 100%;", css)
        self.assertNotIn(".opal-main table {\n    width: max-content !important;", css)
        self.assertNotIn("min-width: 680px; font-size: .84rem;", css)

    def test_wide_tables_still_have_explicit_scroll_contract(self):
        css = self.source("static/css/opal_theme_system.css")
        self.assertIn(".opal-mobile-scroll-table > table", css)
        self.assertIn(".opal-timetable-matrix-wrap > table", css)
        self.assertIn(".opal-table-scroll > table", css)
        self.assertIn("min-width:680px !important", css)

    def test_r143_cache_busting_is_deployed(self):
        base = self.source("templates/base/base.html")
        print_template = self.source("templates/parent_portal/family_statement_print.html")
        self.assertIn("opal-131.7-r143-ui-consistency-audit", base)
        self.assertIn("opal-131.7-r143-ui-consistency-audit", print_template)
